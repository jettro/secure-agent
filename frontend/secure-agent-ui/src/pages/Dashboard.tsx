import {useState, useRef, useEffect} from "react";
import {queryAgent, resetAgent} from "../api/agentService.ts";

interface DashboardProps {
    user: string;
    token: string;
}

const Dashboard = ({user}: DashboardProps) => {
    const [query, setQuery] = useState("");
    const [responses, setResponses] = useState<{ query: string; message: string }[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const chatBodyRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Scroll to bottom on new message
        if (chatBodyRef.current) {
            chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
        }
    }, [responses, loading]);

    const handleSend = async () => {
        if (!query.trim()) return;
        setLoading(true);

        try {
            setError(null)
            const message = await queryAgent(query);
            setResponses((prev) => [...prev, {query, message: message}]);
            setQuery(""); // Clear the input
        } catch (error) {
            // @ts-expect-error The error does contain a message
            setError(error?.message || "An error occurred while fetching the response. Please try again.");
            console.error("Error:", error);
        } finally {
            setLoading(false)
        }
    };

    const handleReset = async () => {
        setLoading(true);
        try {
            setError(null);
            const message = await resetAgent();
            setResponses((prev) => [{query, message: message}]);
        } catch (error) {
            // @ts-expect-error The error does contain a message
            setError(error?.message || "An error occurred while resetting the agent. Please try again.");
            console.error("Error:", error);
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container" style={{marginTop: "4rem", maxWidth: 600}}>
            <div className="card shadow">
                <div className="card-header d-flex justify-content-between align-items-center">
                    <span>Secure Agent Chat</span>
                    <button className="btn btn-sm btn-outline-danger" onClick={handleReset} disabled={loading}>
                        Reset
                    </button>
                </div>
                <div
                    className="card-body"
                    ref={chatBodyRef}
                    style={{height: "350px", overflowY: "auto", background: "#f8f9fa"}}
                >
                    <div className="mb-2 text-muted">Welcome, {user}!</div>
                    {error && <div className="alert alert-danger py-1">{error}</div>}
                    {responses.map((res, index) => (
                        <div key={index} className="mb-3">
                            <div>
                                <span className="fw-bold text-primary">You:</span> {res.query}
                            </div>
                            <div>
                                <span className="fw-bold text-success">Agent:</span> {res.message}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="d-flex justify-content-center my-3">
                            <div className="spinner-border text-primary" role="status" aria-label="Loading...">
                                <span className="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    )}
                </div>
                <div className="card-footer d-flex">
                    <input
                        type="text"
                        className="form-control me-2"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Type your query..."
                        onKeyDown={e => e.key === "Enter" && !loading && handleSend()}
                        disabled={loading}
                    />
                    <button className="btn btn-primary" onClick={handleSend} disabled={loading}>
                        {loading ? (
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        ) : "Send"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;