import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { request, gql } from 'graphql-request';

const GRAPHQL_ENDPOINT = 'http://localhost:8001/graphql';

const DRILL_QUERY = gql`
  query RevenueBreakdown($date: Date!) {
    revenueBreakdownByDate(date: $date) {
      paymentMethods { label value }
      transactionTypes { label value }
      currencies { label value }
    }
  }
`;

const DRILL_OPTIONS = ['Payment Method', 'Currency', 'Transaction Type'];

export default function RevenueChartWithDrilldown() {
  const [chartData, setChartData] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [drillOptionsData, setDrillOptionsData] = useState([]);
  const [drillType, setDrillType] = useState(null);

  const fetchData = async (date) => {
    const data = await request(GRAPHQL_ENDPOINT, DRILL_QUERY, { date });
    setChartData(data.revenueBreakdownByDate.paymentMethods);
    setDrillOptionsData(data.revenueBreakdownByDate);
  };

  useEffect(() => {
    fetchData('2025-07-20'); // default
  }, []);

  const chartOptions = {
    title: { text: 'Revenue by Payment Method' },
    tooltip: { trigger: 'item' },
    xAxis: { type: 'category', data: chartData.map(item => item.label) },
    yAxis: { type: 'value' },
    series: [
      {
        data: chartData.map(item => item.value),
        type: 'bar',
      },
    ],
  };

  const handleChartClick = (params) => {
    setSelectedDate('2025-07-20'); // use the actual clicked date if dynamic
    setDialogOpen(true);
  };

  const handleDrillSelect = (type) => {
    setDrillType(type);
    setDialogOpen(false);
  };

  const renderDrillChart = () => {
    if (!drillType) return null;

    const dataMap = {
      'Payment Method': drillOptionsData.paymentMethods,
      'Currency': drillOptionsData.currencies,
      'Transaction Type': drillOptionsData.transactionTypes,
    };

    const drillData = dataMap[drillType];

    return (
      <ReactECharts
        option={{
          title: { text: `Drilldown by ${drillType}` },
          tooltip: { trigger: 'item' },
          xAxis: { type: 'category', data: drillData.map(i => i.label) },
          yAxis: { type: 'value' },
          series: [
            {
              type: 'bar',
              data: drillData.map(i => i.value),
            },
          ],
        }}
        style={{ height: 400 }}
      />
    );
  };

  return (
    <div className="p-4">
      <ReactECharts
        option={chartOptions}
        onEvents={{ click: handleChartClick }}
        style={{ height: 400 }}
      />

      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-[300px] text-center">
            <h2 className="text-lg font-semibold mb-4">Drilldown By</h2>
            {DRILL_OPTIONS.map((option) => (
              <button
                key={option}
                onClick={() => handleDrillSelect(option)}
                className="block w-full bg-blue-600 hover:bg-blue-700 text-white py-2 my-2 rounded"
              >
                {option}
              </button>
            ))}
            <button
              onClick={() => setDialogOpen(false)}
              className="mt-2 text-sm text-gray-600 hover:underline"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {renderDrillChart()}
    </div>
  );
}
