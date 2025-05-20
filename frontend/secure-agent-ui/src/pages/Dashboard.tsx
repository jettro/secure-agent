import {useState} from "react";
import {queryAgent} from "../api/agentService.ts";

interface DashboardProps {
    user: string;
    token: string;
}

const Dashboard = ({user}: DashboardProps) => {
    const [query, setQuery] = useState("");
    const [responses, setResponses] = useState<{ query: string; message: string }[]>([]);
    const [error, setError] = useState<string | null>(null);

    const handleSend = async () => {
        if (!query.trim()) return;

        try {
            setError(null)
            const message = await queryAgent(query);
            setResponses((prev) => [...prev, {query, message: message}]);
            setQuery(""); // Clear the input
        } catch (error) {
            // @ts-expect-error The error does contain a message
            setError(error?.message || "An error occurred while fetching the response. Please try again.");
            console.error("Error:", error);
        }
    };

    return (
        <div style={{marginTop: "4rem"}}>
            <h2>Dashboard</h2>
            <p>Welcome, {user}!</p>
            {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}
            <div>
                <div style={{marginBottom: "1rem"}}>
                    {responses.map((res, index) => (
                        <div key={index} style={{marginBottom: "0.5rem"}}>
                            <strong>You:</strong> {res.query}
                            <br/>
                            <strong>Agent:</strong> {res.message}
                        </div>
                    ))}
                </div>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Type your query..."
                    style={{marginRight: "0.5rem", padding: "0.5rem", width: "70%"}}
                />
                <button onClick={handleSend} style={{padding: "0.5rem"}}>
                    Send
                </button>
            </div>
        </div>
    );
};

export default Dashboard;