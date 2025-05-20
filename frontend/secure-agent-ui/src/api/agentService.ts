import axiosInstance from "./axiosInstance";

export const queryAgent = async (query: string): Promise<string> => {
    try {
        // const body = {"query": query}
        const response = await axiosInstance.post(
            "/query",
            {query},
            {
                headers: {},
            }
        );
        return response.data.response;
    } catch (error) {
        if (error.response && error.response.status === 401) {
            throw new Error(error.response.data.detail || "Unauthorized access");
        }
        throw new Error(error.message || "Failed to fetch response");
    }
};

export const resetAgent = async (): Promise<string> => {
    try {
        const response = await axiosInstance.post(
            "/reset",
            {},
            {
                headers: {},
            }
        );
        return response.data.response;
    } catch (error) {
        if (error.response && error.response.status === 401) {
            throw new Error(error.response.data.detail || "Unauthorized access");
        }
        throw new Error(error.message || "Failed to reset agent");
    }
}