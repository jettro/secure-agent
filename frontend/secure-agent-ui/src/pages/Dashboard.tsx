interface DashboardProps {
  user: string;
}

const Dashboard = ({ user }: DashboardProps) => (
  <div>
    <h2>Dashboard</h2>
    <p>Welcome, {user}!</p>
  </div>
);

export default Dashboard;