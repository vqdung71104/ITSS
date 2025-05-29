# Copyright © 2024 Pathway

from __future__ import annotations

from pathway.internals import reducers, udfs, universes
from pathway.internals.api import (
    Pointer,
    PyObjectWrapper,
    SqlWriterInitMode,
    wrap_py_object,
)
from pathway.internals.common import (
    apply,
    apply_async,
    apply_with_type,
    assert_table_has_schema,
    cast,
    coalesce,
    declare_type,
    fill_error,
    if_else,
    iterate,
    make_tuple,
    require,
    table_transformer,
    unwrap,
)
from pathway.internals.config import set_license_key, set_monitoring_config
from pathway.internals.custom_reducers import BaseCustomAccumulator
from pathway.internals.datetime_types import DateTimeNaive, DateTimeUtc, Duration
from pathway.internals.decorators import (
    attribute,
    input_attribute,
    input_method,
    method,
    output_attribute,
    transformer,
)
from pathway.internals.errors import global_error_log, local_error_log
from pathway.internals.expression import (
    ColumnExpression,
    ColumnReference,
    ReducerExpression,
)
from pathway.internals.groupbys import GroupedJoinResult, GroupedTable
from pathway.internals.interactive import LiveTable, enable_interactive_mode
from pathway.internals.join_mode import JoinMode
from pathway.internals.joins import (
    Joinable,
    JoinResult,
    join,
    join_inner,
    join_left,
    join_outer,
    join_right,
)
from pathway.internals.json import Json
from pathway.internals.monitoring import MonitoringLevel
from pathway.internals.operator import iterate_universe
from pathway.internals.row_transformer import ClassArg
from pathway.internals.run import run, run_all
from pathway.internals.schema import (
    ColumnDefinition,
    Schema,
    SchemaProperties,
    column_definition,
    schema_builder,
    schema_from_csv,
    schema_from_dict,
    schema_from_types,
)
from pathway.internals.sql import sql
from pathway.internals.table import Table, groupby
from pathway.internals.table_like import TableLike
from pathway.internals.table_slice import TableSlice
from pathway.internals.thisclass import left, right, this
from pathway.internals.udfs import UDF, udf
from pathway.internals.version import __version__
from pathway.internals.yaml_loader import load_yaml

__all__ = [
    "JoinMode",
    "ClassArg",
    "declare_type",
    "cast",
    "reducers",
    "apply",
    "udf",
    "UDF",
    "apply_async",
    "apply_with_type",
    "attribute",
    "input_attribute",
    "input_method",
    "iterate",
    "method",
    "output_attribute",
    "transformer",
    "iterate_universe",
    "schema_from_types",
    "GroupedTable",
    "GroupedJoinResult",
    "JoinResult",
    "IntervalJoinResult",
    "Table",
    "TableLike",
    "ColumnReference",
    "ColumnExpression",
    "ReducerExpression",
    "Schema",
    "Pointer",
    "PyObjectWrapper",
    "wrap_py_object",
    "MonitoringLevel",
    "WindowJoinResult",
    "this",
    "left",
    "right",
    "Joinable",
    "coalesce",
    "require",
    "if_else",
    "make_tuple",
    "sql",
    "run",
    "run_all",
    "__version__",
    "universes",
    "udfs",
    "AsofJoinResult",
    "schema_builder",
    "column_definition",
    "TableSlice",
    "unwrap",
    "fill_error",
    "SchemaProperties",
    "schema_from_csv",
    "schema_from_dict",
    "assert_table_has_schema",
    "DateTimeNaive",
    "DateTimeUtc",
    "Duration",
    "Json",
    "table_transformer",
    "BaseCustomAccumulator",
    "join",
    "join_inner",
    "join_left",
    "join_right",
    "join_outer",
    "groupby",
    "enable_interactive_mode",
    "LiveTable",
    "set_license_key",
    "set_monitoring_config",
    "global_error_log",
    "local_error_log",
    "ColumnDefinition",
    "load_yaml",
    "SqlWriterInitMode",
]

# Copyright © 2024 Pathway

from __future__ import annotations

import json

import boto3
import boto3.session

from pathway.internals import api, schema
from pathway.internals.table import Table
from pathway.internals.trace import trace_user_frame

S3_PATH_PREFIXES = ["s3://", "s3a://"]
S3_DEFAULT_REGION = "us-east-1"
S3_LOCATION_FIELD = "LocationConstraint"


class AwsS3Settings:
    """Stores Amazon S3 connection settings. You may also use this class to store
    configuration settings for any custom S3 installation, however you will need to
    specify the region and the endpoint.

    Args:
        bucket_name: Name of S3 bucket.
        access_key: Access key for the bucket.
        secret_access_key: Secret access key for the bucket.
        with_path_style: Whether to use path-style requests.
        region: Region of the bucket.
        endpoint: Custom endpoint in case of self-hosted storage.
        session_token: Session token, an alternative way to authenticate to S3.
    """

    @trace_user_frame
    def __init__(
        self,
        *,
        bucket_name=None,
        access_key=None,
        secret_access_key=None,
        with_path_style=False,
        region=None,
        endpoint=None,
        session_token=None,
    ):
        self._bucket_name = bucket_name
        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._session_token = session_token
        self._with_path_style = with_path_style
        self._region = region
        self._endpoint = endpoint

    @property
    def settings(self) -> api.AwsS3Settings:
        return api.AwsS3Settings(
            self._bucket_name,
            self._access_key,
            self._secret_access_key,
            self._with_path_style,
            self._region,
            self._endpoint,
            self._session_token,
        )

    @classmethod
    def new_from_path(cls, s3_path: str):
        """
        Constructs settings from S3 path. The engine will look for the credentials in
        environment variables and in local AWS profiles. It will also automatically
        detect the region of the bucket.

        This method may fail if there are no credentials or they are incorrect. It may
        also fail if the bucket does not exist.

        Args:
            s3_path: full path to the object in the form ``s3://<bucket_name>/<path>``.

        Returns:
            Configuration object.
        """
        for s3_path_prefix in S3_PATH_PREFIXES:
            starts_with_prefix = s3_path.startswith(s3_path_prefix)
            has_extra_chars = len(s3_path) > len(s3_path_prefix)
            if not starts_with_prefix or not has_extra_chars:
                continue
            bucket = s3_path[len(s3_path_prefix) :].split("/")[0]

            # the crate we use on the Rust-engine side can't detect the location
            # of a bucket, so it's done on the Python side
            s3_client = boto3.client("s3")
            location_response = s3_client.get_bucket_location(Bucket=bucket)

            # Buckets in Region us-east-1 have a LocationConstraint of None
            location_constraint = location_response[S3_LOCATION_FIELD]
            if location_constraint is None:
                region = S3_DEFAULT_REGION
            else:
                region = location_constraint.split("|")[0]

            return cls(
                bucket_name=bucket,
                region=region,
            )

        # If it doesn't start with a valid S3 prefix, it's not a full S3 path
        raise ValueError(f"Incorrect S3 path: {s3_path}")

    def authorize(self):
        if self._access_key is not None and self._secret_access_key is not None:
            return

        # DeltaLake underlying AWS S3 library may fail to deduce the credentials, so
        # we use boto3 to do that, which is more reliable
        # Related github issue: https://github.com/delta-io/delta-rs/issues/854
        session = boto3.session.Session()
        creds = session.get_credentials()
        if creds.access_key is not None and creds.secret_key is not None:
            self._access_key = creds.access_key
            self._secret_access_key = creds.secret_key
        elif creds.token is not None:
            self._session_token = creds.token


def is_s3_path(path: str) -> bool:
    for s3_path_prefix in S3_PATH_PREFIXES:
        if path.startswith(s3_path_prefix):
            return True
    return False


def _format_output_value_fields(table: Table) -> list[api.ValueField]:
    value_fields = []
    for column_name, column_data in table.schema.columns().items():
        value_field = api.ValueField(
            column_name,
            column_data.dtype.to_engine(),
        )
        value_field.set_metadata(
            json.dumps(column_data.to_json_serializable_dict(), sort_keys=True)
        )
        value_fields.append(value_field)

    return value_fields


def _form_value_fields(schema: type[schema.Schema]) -> list[api.ValueField]:
    schema.default_values()
    default_values = schema.default_values()
    result = []

    types = {name: dtype.to_engine() for name, dtype in schema._dtypes().items()}

    for f in schema.column_names():
        dtype = types.get(f, api.PathwayType.ANY)
        value_field = api.ValueField(f, dtype)
        if f in default_values:
            value_field.set_default(default_values[f])
        result.append(value_field)

    return result

# Copyright © 2024 Pathway

import pickle
from abc import ABC, abstractmethod
from collections import Counter
from typing import ParamSpec, Protocol, TypeVar

from typing_extensions import Self

from pathway.internals import api, expression as expr
from pathway.internals.column import ColumnExpression
from pathway.internals.common import apply_with_type
from pathway.internals.reducers import StatefulManyReducer
from pathway.internals.shadows.inspect import signature

P = ParamSpec("P")


S = TypeVar("S", bound=api.Value)
V1 = TypeVar("V1", bound=api.Value)
V2 = TypeVar("V2", bound=api.Value)


def mark_stub(fun):
    fun.__pw_stub = True
    return fun


class ReducerProtocol(Protocol):
    def __call__(
        self,
        *args: expr.ColumnExpression | api.Value | tuple[expr.ColumnExpression, ...],
    ) -> expr.ColumnExpression: ...


def stateful_many(
    combine_many: api.CombineMany[S],
) -> ReducerProtocol:
    """Decorator used to create custom stateful reducers.

    A function wrapped with it has to process the previous state and a list of updates
    at a specific time. It has to return a new state. The updates are grouped in batches
    (all updates in a batch have the same processing time, the function is called once
    per batch) and the batches enter the function in order of increasing processing time.

    Example:

    Create a table where ``__time__`` column simulates processing time assigned
    to entries when they enter pathway:

    >>> import pathway as pw
    >>> table = pw.debug.table_from_markdown(
    ...     '''
    ...      a | b | __time__
    ...      3 | 1 |     2
    ...      4 | 1 |     2
    ...     13 | 2 |     2
    ...     16 | 2 |     4
    ...      2 | 2 |     6
    ...      4 | 1 |     6
    ... '''
    ... )

    Now create a custom stateful reducer. It is going to compute a weird sum.
    It is a sum of even entries incremented by 1 and unchanged odd entries.

    >>> @pw.reducers.stateful_many
    ... def weird_sum(state: int | None, rows: list[tuple[list[int], int]]) -> int:
    ...     if state is None:
    ...         state = 0
    ...     for row, cnt in rows:
    ...         value = row[0]
    ...         if value % 2 == 0:
    ...             state += value + 1
    ...         else:
    ...             state += value
    ...     return state

    ``state`` is ``None`` when the function is called for the first time for a given group.
    To compute a weird sum, you should set it to 0 then.

    ``row`` is a list of values passed to the reducer. When the reducer is called as
    ``weird_sum(pw.this.a)``, the list has only one element, i.e. value from the column a.
    ``cnt`` tells whether the row is an insertion (``cnt == 1``) or deletion (``cnt == -1``).
    You can learn more `here </developers/user-guide/introduction/concepts#the-output-is-a-data-stream>`_.

    You can now use the reducer in ``reduce`` operator and compute the result:

    >>> result = table.groupby(pw.this.b).reduce(pw.this.b, s=weird_sum(pw.this.a))
    >>> pw.debug.compute_and_print(result, include_id=False)
    b | s
    1 | 13
    2 | 33

    ``weird_sum`` is called 2 times for group 1 (at processing times 2 and 6) and 3 times
    for group 2 (at processing times 2, 4, 6).
    """

    def wrapper(
        *args: expr.ColumnExpression | api.Value | tuple[expr.ColumnExpression, ...],
    ) -> expr.ColumnExpression:
        return expr.ReducerExpression(StatefulManyReducer(combine_many), *args)

    return wrapper


class CombineSingle(Protocol[S, P]):
    def __call__(self, state: S | None, /, *args: P.args, **kwargs: P.kwargs) -> S: ...


def stateful_single(combine_single: CombineSingle[S, ...]) -> ReducerProtocol:
    """Decorator used to create custom stateful reducers.

    A function wrapped with it has to process the previous state and a single update.
    It has to return a new state. The function is called with entries in order of
    increasing processing time. If there are multiple entries with the same processing
    time, their order is unspecified.

    The function can only be used on tables with insertions only (no updates or deletions).
    If you need to handle updates/deletions, see
    `stateful_many </developers/api-docs/reducers#pathway.reducers.stateful_many>`_.

    Example:

    Create a table where ``__time__`` column simulates processing time assigned
    to entries when they enter pathway:

    >>> import pathway as pw
    >>> table = pw.debug.table_from_markdown(
    ...     '''
    ...      a | b | __time__
    ...      3 | 1 |     2
    ...      4 | 1 |     2
    ...     13 | 2 |     2
    ...     16 | 2 |     4
    ...      2 | 2 |     6
    ...      4 | 1 |     6
    ... '''
    ... )

    Create a custom stateful reducer. It is going to compute a weird sum.
    It is a sum of even entries incremented by 1 and unchanged odd entries.

    >>> @pw.reducers.stateful_single
    ... def weird_sum(state: int | None, value) -> int:
    ...     if state is None:
    ...         state = 0
    ...     if value % 2 == 0:
    ...         state += value + 1
    ...     else:
    ...         state += value
    ...     return state

    ``state`` is ``None`` when the function is called for the first time for a given group.
    To compute a weird sum, you should set it to 0 then.

    You can now use the reducer in ``reduce`` operator and compute the result:

    >>> result = table.groupby(pw.this.b).reduce(pw.this.b, s=weird_sum(pw.this.a))
    >>> pw.debug.compute_and_print(result, include_id=False)
    b | s
    1 | 13
    2 | 33
    """

    def wrapper(state: S | None, rows: list[tuple[list[api.Value], int]]) -> S:
        for row, count in rows:
            assert count > 0
            for _ in range(count):
                state = combine_single(state, *row)
        assert state is not None
        return state

    return stateful_many(wrapper)


class BaseCustomAccumulator(ABC):
    """Utility class for defining custom accumulators, used for stateful reducers.
    Custom accumulators should inherit from this class, and should implement ``from_row``,
    ``update`` and ``compute_result``. Optionally ``neutral`` and ``retract`` can be provided
    for more efficient processing on streams with changing data. Additionally, ``serialize``
    and ``deserialize`` can be customized. By default they use ``pickle`` module,
    but if the accumulator state is serializable to pathway value type in an easier way,
    this can be overwritten.

    >>> import pathway as pw
    >>> class CustomAvgAccumulator(pw.BaseCustomAccumulator):
    ...   def __init__(self, sum, cnt):
    ...     self.sum = sum
    ...     self.cnt = cnt
    ...
    ...   @classmethod
    ...   def from_row(self, row):
    ...     [val] = row
    ...     return CustomAvgAccumulator(val, 1)
    ...
    ...   def update(self, other):
    ...     self.sum += other.sum
    ...     self.cnt += other.cnt
    ...
    ...   def compute_result(self) -> float:
    ...     return self.sum / self.cnt
    >>> import sys; sys.modules[__name__].CustomAvgAccumulator = CustomAvgAccumulator # NODOCS
    >>> custom_avg = pw.reducers.udf_reducer(CustomAvgAccumulator)
    >>> t1 = pw.debug.table_from_markdown('''
    ... age | owner | pet | price
    ... 10  | Alice | dog | 100
    ... 9   | Bob   | cat | 80
    ... 8   | Alice | cat | 90
    ... 7   | Bob   | dog | 70
    ... ''')
    >>> t2 = t1.groupby(t1.owner).reduce(t1.owner, avg_price=custom_avg(t1.price))
    >>> pw.debug.compute_and_print(t2, include_id=False)
    owner | avg_price
    Alice | 95.0
    Bob   | 75.0
    """

    @classmethod
    @mark_stub
    def neutral(cls) -> Self:
        """Neutral element of the accumulator (aggregation of an empty list).

        This function is optional, and allows for more efficient processing on streams
        with changing data."""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_row(cls, row: list[api.Value]) -> Self:
        """Construct the accumulator from a row of data.
        Row will be passed as a list of values.

        This is a mandatory function."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, other: Self) -> None:
        """Update the accumulator with another one.
        Method does not need to return anything, the change should be in-place.

        This is a mandatory function."""
        raise NotImplementedError()

    @mark_stub
    def retract(self, other: Self) -> None:
        """Update the accumulator by removing the value of another one.

        This function is optional, and allows more efficient reductions on streams
        with changing data.
        """
        raise NotImplementedError()

    @abstractmethod
    def compute_result(self) -> api.Value:
        """Mandatory function to finalize computation.
        Used to extract answer from final state of accumulator.

        Narrowing the type of this function helps better type the output of the reducer.
        """
        raise NotImplementedError()

    @classmethod
    @mark_stub
    def sort_by(cls, row: list[api.Value]):
        """Value to sort rows within a single batch by.
        This function is optional. If not defined, the order of rows within a single batch is unspecified.
        """
        raise NotImplementedError()

    def serialize(self) -> api.Value:
        """Serialize state to pathway value type."""
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, val: api.Value):
        """Deserialize state from pathway value type."""
        assert isinstance(val, bytes)
        return pickle.loads(val)


def udf_reducer(reducer_cls: type[BaseCustomAccumulator]):
    """Decorator for defining stateful reducers. Requires custom accumulator as an argument.
    Custom accumulator should implement ``from_row``, ``update`` and ``compute_result``.
    Optionally ``neutral`` and ``retract`` can be provided for more efficient processing on
    streams with changing data.

    >>> import pathway as pw
    >>> class CustomAvgAccumulator(pw.BaseCustomAccumulator):
    ...   def __init__(self, sum, cnt):
    ...     self.sum = sum
    ...     self.cnt = cnt
    ...
    ...   @classmethod
    ...   def from_row(self, row):
    ...     [val] = row
    ...     return CustomAvgAccumulator(val, 1)
    ...
    ...   def update(self, other):
    ...     self.sum += other.sum
    ...     self.cnt += other.cnt
    ...
    ...   def compute_result(self) -> float:
    ...     return self.sum / self.cnt
    >>> import sys; sys.modules[__name__].CustomAvgAccumulator = CustomAvgAccumulator # NODOCS
    >>> custom_avg = pw.reducers.udf_reducer(CustomAvgAccumulator)
    >>> t1 = pw.debug.table_from_markdown('''
    ... age | owner | pet | price
    ... 10  | Alice | dog | 100
    ... 9   | Bob   | cat | 80
    ... 8   | Alice | cat | 90
    ... 7   | Bob   | dog | 70
    ... ''')
    >>> t2 = t1.groupby(t1.owner).reduce(t1.owner, avg_price=custom_avg(t1.price))
    >>> pw.debug.compute_and_print(t2, include_id=False)
    owner | avg_price
    Alice | 95.0
    Bob   | 75.0
    """
    neutral_available = _is_overridden(reducer_cls, "neutral")
    retract_available = _is_overridden(reducer_cls, "retract")
    sort_by_available = _is_overridden(reducer_cls, "sort_by")

    def wrapper(*args: expr.ColumnExpression | api.Value) -> ColumnExpression:
        @stateful_many
        def stateful_wrapper(
            packed_state: tuple[api.Value, tuple, int] | None,
            rows: list[tuple[list[api.Value], int]],
        ) -> tuple[api.Value, tuple, int] | None:
            if packed_state is not None:
                serialized_state, _positive_updates_tuple, _cnt = packed_state
                state = reducer_cls.deserialize(serialized_state)
                _positive_updates = list(_positive_updates_tuple)
            else:
                state = None
            positive_updates: list[tuple[api.Value, ...]] = []
            negative_updates = []
            for row, count in rows:
                if count > 0:
                    positive_updates.extend([tuple(row)] * count)
                else:
                    negative_updates.extend([tuple(row)] * (-count))

            if not retract_available and len(negative_updates) > 0:
                if state is not None:
                    assert _positive_updates is not None
                    positive_updates.extend(_positive_updates)
                    _positive_updates = []
                    state = None
                acc = Counter(positive_updates)
                acc.subtract(negative_updates)
                assert all(x >= 0 for x in acc.values())
                positive_updates = list(acc.elements())
                negative_updates = []

            if state is None:
                if neutral_available:
                    state = reducer_cls.neutral()
                    _positive_updates = []
                    _cnt = 0
                elif len(positive_updates) == 0:
                    if len(negative_updates) == 0:
                        return None
                    else:
                        raise ValueError(
                            "Unable to process negative update with this stateful reducer."
                        )
                else:
                    if sort_by_available:
                        positive_updates.sort(
                            key=lambda x: reducer_cls.sort_by(list(x))
                        )
                    state = reducer_cls.from_row(list(positive_updates[0]))
                    if not retract_available:
                        _positive_updates = positive_updates[0:1]
                        _cnt = 0
                    else:
                        _positive_updates = []
                        _cnt = 1
                    positive_updates = positive_updates[1:]

            updates = [(row_up, False) for row_up in positive_updates] + [
                (row_up, True) for row_up in negative_updates
            ]

            if sort_by_available:
                updates.sort(key=lambda x: (reducer_cls.sort_by(list(x[0])), x[1]))
                # insertions first for a given `sort_by` value to be "compatible" with no `sort_by` situation

            for row_up, is_retraction in updates:
                if is_retraction:
                    if not retract_available:
                        raise ValueError(
                            "Unable to process negative update with this stateful reducer."
                        )
                    else:
                        _cnt -= 1
                    val = reducer_cls.from_row(list(row_up))
                    state.retract(val)
                else:
                    if not retract_available:
                        _positive_updates.append(row_up)
                    else:
                        _cnt += 1
                    val = reducer_cls.from_row(list(row_up))
                    state.update(val)

            _positive_updates_tuple = tuple(tuple(x) for x in _positive_updates)
            if retract_available and _cnt == 0:
                # this is fine in this setting, where we process values one by one
                # if this ever becomes accumulated in a tree, we have to handle
                # (A-B) updates, so we have to distinguish `0` from intermediate states
                # accumulating weighted count (weighted by hash) should do fine here
                return None
            return state.serialize(), _positive_updates_tuple, _cnt

        def extractor(packed: tuple):
            deserialized = reducer_cls.deserialize(packed[0])
            assert isinstance(deserialized, reducer_cls)
            return deserialized.compute_result()

        return apply_with_type(
            extractor,
            signature(reducer_cls.compute_result).return_annotation,
            stateful_wrapper(*args),
        )

    return wrapper


def _is_overridden(cls: type[BaseCustomAccumulator], name: str) -> bool:
    assert hasattr(BaseCustomAccumulator, name)
    return not hasattr(getattr(cls, name), "__pw_stub")

