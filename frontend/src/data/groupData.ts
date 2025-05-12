
import axiosInstance from "../axios-config";
import { Group, GroupMember } from "../components/groups/GroupCard"
let cachedGroups: Group[] = [];
let lastFetchTime: number = 0;
const CACHE_DURATION = 100* 60 * 1000; // 5 phút cache

export const getGroups = async (forceRefresh = false): Promise<Group[]> => {
    const now = Date.now();
    
    // Nếu có cache và chưa hết hạn, và không yêu cầu refresh
    if (cachedGroups.length > 0 && now - lastFetchTime < CACHE_DURATION && !forceRefresh) {
        return cachedGroups;
    }

    try {
        console.log("Fetching groups from API...");
        const response = await axiosInstance.get("/groups/");

        cachedGroups = response.data.map((group: any) => ({
            id: group.id,
            name: group.name,
            leader: group.leader_name,
            projectId: group.project_id,
            projectTitle: group.project_title,
            members: group.members.map((member: any) => ({
                id: member._id,
                name: member.ho_ten,
                avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(
                    member.ho_ten
                  )}&background=random`,
            })),
            progress: 50,
            hasUnreadMessages: true,
            
        }));
        console.log("Cached groups:", cachedGroups);
        lastFetchTime = now;
        return cachedGroups;
    } catch (error) {
        console.error("Error fetching groups:", error);
        // Nếu có lỗi nhưng đã có cache trước đó, trả về cache cũ
        if (cachedGroups.length > 0) {
            console.warn("Using cached groups due to API error");
            return cachedGroups;
        }
        throw error;
    }
};

export const getCachedGroups = (): Group[] => {
    return cachedGroups;
};
