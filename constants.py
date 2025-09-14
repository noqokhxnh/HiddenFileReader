"""
Constants for the HiddenFileReader application.
"""

# Maximum file size to process (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Text constants for UI
TEXT_VI = {
    "app_title": "🔍 HIDDENFILEREADER",
    "input_project_path": "📂 Nhập đường dẫn thư mục dự án: ",
    "done": "\n🎉 Hoàn thành! File hidden_dump.txt đã sẵn sàng.",
    "error": "\n💥 Có lỗi xảy ra trong quá trình xử lý.",
    "analyzing": "🔍 Đang phân tích dự án tại: ",
    "scanning": "🔍 Đang quét thư mục...",
    "included_types": "📁 Các loại tệp sẽ được bao gồm: ",
    "generating_tree": "📁 Đang tạo cây thư mục...",
    "processing_files": "📄 Đang xử lý các tệp ẩn...",
    "skip_large": "⚠️  Bỏ qua {file} (kích thước {size} byte > giới hạn {limit} byte)",
    "skip_binary": "🚫 Bỏ qua {file} (tệp nhị phân)",
    "processing": "  📝 Xử lý: {file}",
    "success": "✅ Thành công! Đã tạo file: ",
    "summary": "📊 Thống kê:",
    "file_count": "   - Số file đã xử lý: {count}",
    "size": "   - Kích thước file đầu ra: {size} ký tự (~{kb} KB)",
    "line_count": "   - Tổng số dòng: {lines}",
    "write_error": "❌ Lỗi ghi file: {error}",
    "not_found": "❌ Lỗi: Thư mục '{path}' không tồn tại!",
}

TEXT_EN = {
    "app_title": "🔍 HIDDENFILEREADER",
    "input_project_path": "📂 Enter the project folder path: ",
    "done": "\n🎉 Done! The hidden_dump.txt file is ready.",
    "error": "\n💥 An error occurred during processing.",
    "analyzing": "🔍 Analyzing project at: ",
    "scanning": "🔍 Scanning directories...",
    "included_types": "📁 File types included: ",
    "generating_tree": "📁 Generating directory tree...",
    "processing_files": "📄 Processing hidden files...",
    "skip_large": "⚠️  Skipping {file} (size {size} bytes > limit {limit} bytes)",
    "skip_binary": "🚫 Skipping {file} (binary file)",
    "processing": "  📝 Processing: {file}",
    "success": "✅ Success! File created: ",
    "summary": "📊 Summary:",
    "file_count": "   - Files processed: {count}",
    "size": "   - Output size: {size} characters (~{kb} KB)",
    "line_count": "   - Total lines: {lines}",
    "write_error": "❌ Error writing file: {error}",
    "not_found": "❌ Error: Folder '{path}' not found!",
}