import React, { useState, useEffect } from "react";
import { fetchCompanies, fetchCompanyData } from "./api";

// Add this import at the top if you want to use a simple chart library
// npm install chart.js react-chartjs-2
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function App() {
  const [companies, setCompanies] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyData, setCompanyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [companiesLoading, setCompaniesLoading] = useState(true);

  // Load company list on mount
  useEffect(() => {
    async function loadCompanies() {
      setCompaniesLoading(true);
      const data = await fetchCompanies();
      console.log("Loaded companies:", data);
      setCompanies(data.companies);
      setLastUpdated(data.generated_at)
      setCompaniesLoading(false);
    }
    
    loadCompanies();
  }, []);

  // When a company is selected, fetch its details
  const handleSelectCompany = async (company) => {
    setSelectedCompany(company);
    setLoading(true);
    console.log("Fetching data for", company.slug);
    const data = await fetchCompanyData(company.slug);
    setCompanyData(data);
    setLoading(false);
  };

  const calculateStockPriceChange = () => {
    if (!companyData?.stock?.history) return null;

    const prices = companyData.stock.history;
    const latestPrice = prices[prices.length - 1]?.close;
    const previousPrice = prices[prices.length - 2]?.close;

    if (latestPrice && previousPrice) {
      const change = ((latestPrice - previousPrice) / previousPrice) * 100;
      return change.toFixed(2);
    }

    return null;
  };

  const formatDateTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZoneName: "short", // Show the time zone for clarity
    });
  };

  // Add this helper to prepare chart data
  const getStockChartData = () => {
    if (!companyData?.stock?.history) return null;
    const history = companyData.stock.history;
    return {
      labels: history.map((item) =>
        new Date(item.date).toLocaleDateString(undefined, { month: "short", day: "numeric" })
      ),
      datasets: [
        {
          label: "Close Price",
          data: history.map((item) => item.close),
          fill: false,
          borderColor: "#6366f1",
          backgroundColor: "#6366f1",
          tension: 0.2,
        },
      ],
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-950 text-white p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Company Tracker</h1>
        <span className="text-gray-400 text-sm">Last updated: {formatDateTime(lastUpdated)}</span>
      </div>

      {/* Layout */}
      <div className="flex gap-8">
        {/* Company List */}
        <div className="w-1/4 border-r border-gray-800 pr-4">
          <h2 className="text-lg font-semibold mb-4">Companies</h2>
          <div
            className="overflow-y-auto max-h-[80vh] custom-scrollbar"
          >
            <ul className="space-y-2">
              {companiesLoading ? (
                <p className="text-gray-500">Loading companies...</p>
              ) : 
              
              companies.length > 0 ? (
                companies.map((company) => (
              <li
                key={company.slug}
                onClick={() => handleSelectCompany(company)}
                className={`p-2 rounded cursor-pointer transition ${
                  selectedCompany?.slug === company.slug
                ? "bg-indigo-600"
                : "hover:bg-gray-800"
                }`}
              >
                {company.name}
              </li>
                ))
              ) :
              
              (
                <p className="text-gray-500">No companies found.</p>
              )}
            </ul>
          </div>
        </div>

        {/* Company Data */}
        <div className="w-3/4">
          {!selectedCompany ? (
            <p className="text-gray-400 text-lg">
              Select a company to view updates
            </p>
          ) : loading ? (
            <p className="text-gray-400">Loading {selectedCompany.name} data...</p>
          ) : companyData ? (
            <div>
              <h2 className="text-2xl font-bold mb-4">{selectedCompany.name}</h2>

              {/* News */}
              {companyData.news && companyData.news.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Latest News</h3>
                  <ul className="space-y-2">
                    {companyData.news.map((item, idx) => (
                      <li key={idx}>
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:underline"
                        >
                          {item.title}
                        </a>{" "}
                        <span className="text-gray-500 text-sm">
                          ({formatDateTime(item.published)})
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Stock Info */}
              {companyData.stock && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Stock</h3>
                  <p>
                    Ticker:{" "}
                    <span className="font-bold">{companyData.stock.ticker}</span>{" "}
                    | Price ({companyData.stock.currency}):{" "}
                    <span className="font-bold">{companyData.stock.latest.close.toFixed(2)}</span>{" "}
                    | Change:{" "}
                    <span
                      className={
                        companyData.stock.change >= 0
                          ? "text-green-400"
                          : "text-red-400"
                      }
                    >
                      {calculateStockPriceChange()}%
                    </span>
                  </p>
                  {/* Stock Price Chart */}
                  {companyData.stock.history && companyData.stock.history.length > 1 && (
                    <div className="mt-4 bg-gray-800 p-4 rounded">
                      <Line
                        data={getStockChartData()}
                        options={{
                          responsive: true,
                          plugins: {
                            legend: { display: false },
                            title: { display: false },
                          },
                          scales: {
                            x: {
                              ticks: { color: "#cbd5e1" },
                              grid: { color: "#334155" },
                            },
                            y: {
                              ticks: { color: "#cbd5e1" },
                              grid: { color: "#334155" },
                            },
                          },
                        }}
                        height={200}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Products */}
              {companyData.product_launches && companyData.product_launches.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Latest Product Launches</h3>
                  <ul className="space-y-2">
                    {companyData.product_launches.map((item, idx) => (
                      <li key={idx}>
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:underline"
                        >
                          {item.title}
                        </a>{" "}
                        <span className="text-gray-500 text-sm">
                          ({formatDateTime(item.published)})
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400">No data available</p>
          )}
        </div>
      </div>
    </div>
  );
}