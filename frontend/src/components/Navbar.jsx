function Navbar({ onUploadClick }) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          
          <h1 className="text-lg font-semibold">Document Processor</h1>
        </div>
        <button 
          onClick={onUploadClick}
          className="flex items-center space-x-2 bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          <span>Upload Documents</span>
        </button>
      </div>
    </header>
  );
}

export default Navbar;