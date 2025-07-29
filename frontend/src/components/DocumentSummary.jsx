import FilePdfIcon from '../icons/FilePdfIcon';
import EyeIcon from '../icons/EyeIcon';

function DocumentSummary() {
  const summaries = [
    {
      name: "annual-report-2023.pdf",
      processedDate: "Jan 15, 2024 at 2:34 PM",
      summary: "This annual report provides a comprehensive overview of the company's financial performance for 2023. Key highlights include a 15% increase in revenue, expansion into three new markets, and successful implementation of sustainability initiatives. The report covers financial statements, market analysis, and strategic outlook for the upcoming year.",
      tags: ["Financial Report", "Revenue Growth", "Market Expansion"]
    }
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold mb-4">Document Summaries</h2>
      
      <div className="space-y-4">
        {summaries.map((item, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <FilePdfIcon className="w-5 h-5" />
                <div>
                  <p className="font-medium text-sm">{item.name}</p>
                  <p className="text-xs text-gray-500">Processed on {item.processedDate}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm">
                  <span>Export</span>
                </button>
                <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm">
                  <span>Share</span>
                </button>
              </div>
            </div>
            
            <div className="mb-3">
              <h4 className="font-medium text-sm mb-2">Summary</h4>
              <p className="text-sm text-gray-700 leading-relaxed">{item.summary}</p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {item.tags.map((tag, tagIndex) => (
                <span 
                  key={tagIndex}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DocumentSummary;