# Chapter 3 covers the basics of data architecture, as storage is the critical underbelly of

Dưới đây là bản dịch và tổng hợp nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide** (Hướng dẫn ra quyết định) tập trung vào các yếu tố kỹ thuật quan trọng của giai đoạn **Ingestion** (Thu thập/Nạp dữ liệu).

---

# Giai đoạn Ingestion: Hướng dẫn Ra quyết định Kỹ thuật

Tài liệu này tóm tắt các cân nhắc kỹ thuật chính trong giai đoạn **Ingestion** (Thu thập dữ liệu), dựa trên nội dung chương về kiến trúc dữ liệu.

## 1. Phân loại luồng Ingestion: Synchronous vs Asynchronous

Việc lựa chọn cách thức thu thập dữ liệu ảnh hưởng trực tiếp đến độ tin cậy và khả năng phục hồi của hệ thống.

### So sánh luồng xử lý

| Đặc điểm | **Synchronous Ingestion** (Đồng bộ) | **Asynchronous Ingestion** (Bất đồng bộ) |
| :--- | :--- | :--- |
| **Cơ chế** | Các giai đoạn (A, B, C) phụ thuộc trực tiếp vào nhau. Nếu A thất bại, B và C không chạy được. | Dựa trên sự kiện (Event-driven). Các giai đoạn có thể chạy song song khi dữ liệu sẵn sàng. |
| **Kiểu xử lý** | Theo **Batch** (Lô). Phải đợi toàn bộ dữ liệu được nạp mới xử lý tiếp. | Theo luỗi **Stream** (Dòng). Dữ liệu được xử lý ngay khi đến. |
| **Rủi ro** | "Hiệu ứng domino": Lỗi ở bước đầu làm tê liệt toàn bộ hệ thống. Phải chạy lại toàn bộ quy trình nếu lỗi. | Lỗi ở một sự kiện không ảnh hưởng đến các sự kiện khác. Cần cơ chế bù đắp (Backfill) nếu cần. |
| **Ví dụ thực tế** | ETL cũ: Extract -> Transform -> Load tuần tự. Quá trình có thể mất >24h và phải chạy lại từ đầu nếu lỗi. | AWS Kinesis Data Streams -> Apache Beam -> S3. Dùng buffer để tránh quá tải. |

### Khi nào nên dùng?
*   **Synchronous:** Khi dữ liệu nhỏ, yêu cầu đơn giản, hoặc hệ thống legacy cũ. **Không khuyến khích** cho hệ thống quy mô lớn.
*   **Asynchronous:** Khi cần độ sẵn sàng cao, xử lý dữ liệu real-time hoặc batch quy mô lớn với khả năng chịu lỗi (Fault tolerance).

---

## 2. Cân nhắc Kỹ thuật chính (Key Engineering Considerations)

### A. Tính năng qua (Throughput) và Khả năng mở rộng (Scalability)
*   **Tại sao dùng?** Để đảm bảo hệ thống không bị nghẽn cổ chai khi dữ liệu tăng trưởng.
*   **Khi nào cần quan tâm?** Khi dữ liệu có tính burst (bùng nổ đột ngột) hoặc khi nguồn dữ liệu (Source) bị downtime và cần backfill lượng lớn dữ liệu.
*   **Giải pháp:**
    *   Dùng **Buffering** (Bộ đệm) như Kafka/Kinesis để hấp thụ các đợt spike dữ liệu.
    *   Ưu tiên dùng **Managed Services** (Dịch vụ được quản lý) để tự động scale (thêm bớt worker/server) thay vì tự build thủ công.

### B. Độ tin cậy (Reliability) và Độ bền (Durability)
*   **Khác biệt:**
    *   **Reliability (Uptime):** Hệ thống có hoạt động liên tục không? (Xử lý failover).
    *   **Durability (Không mất dữ liệu):** Đảm bảo dữ liệu đã thu thập không bị mất hay hỏng.
*   **Trade-off (Đánh đổi):**
    *   Xây dựng hệ thống dự phòng (Redundancy) 24/7 giúp tăng độ tin cậy nhưng chi phí **Cloud và Nhân sự (Lập trình viên/DevOps)** sẽ rất cao.
*   **Lời khuyên:** Đánh giá rủi ro mất dữ liệu. Nếu dữ liệu từ IoT hoặc Cache mà không nạp được thì sẽ mất vĩnh viễn. Đừng cố gắng đảm bảo 100% trong mọi trường hợp (ví dụ: mất điện toàn khu vực), hãy tập trung vào mức độ chịu đựng phù hợp với ngân sách.

### C. Payload (Kiểu dữ liệu tải lên)
Payload là tập dữ liệu bạn đang nạp, bao gồm các đặc điểm sau:

1.  **Kind (Phân loại):**
    *   **Tabular:** Dạng bảng (CSV, Parquet).
    *   **Unstructured:** Ảnh (JPG/PNG), Text, Audio.
    *   *Ảnh hưởng:* Determines how it’s dealt with downstream.

2.  **Shape (Hình dạng/Kích thước chiều):**
    *   Quan trọng cho việc huấn luyện Model hoặc mapping database.
    *   Ví dụ: Tabular (M rows, N columns), Ảnh (Width, Height, RGB depth), Audio (Channels, Sample rate).

3.  **Size (Dung lượng):**
    *   Có thể từ Byte đến Terabyte.
    *   **Giải pháp:** Nén dữ liệu (Compression - ZIP, TAR) hoặc chia nhỏ (Chunking) để dễ truyền tải.

4.  **Schema and Data Types (Lược đồ và Kiểu dữ liệu):**
    *   Rất quan trọng. Nếu Schema không khớp (ví dụ: file CSV nhiều cột hơn database đích), quá trình nạp sẽ thất bại.
    *   **Challenge:** Hiểu rõ Schema của hệ thống nguồn (Source) thường khó khăn do sự khác biệt giữa Object-oriented programming và Database relational.

### D. Schema Evolution (Thay đổi lược đồ)
*   **Vấn đề:** Nguồn dữ liệu thường thay đổi (thêm cột, đổi tên, thay đổi kiểu dữ liệu).
*   **Giải pháp:**
    *   Dùng **Schema Registry** (ví dụ: Confluent Schema Registry) để quản lý version và đảm bảo tương thích giữa Producer và Consumer trong hệ thống Streaming.
    *   Tự động hóa việc phát hiện thay đổi, nhưng cần cảnh báo (Alert) cho Analyst/Data Scientist nếu thay đổi đó làm hỏng báo cáo hiện tại.

---

## 3. Kiểu truy xuất dữ liệu (Push vs Pull vs Poll)

| Mô hình | **Push** | **Pull** | **Poll** |
| :--- | :--- | :--- | :--- |
| **Mô tả** | Nguồn (Source) **gửi** dữ liệu đến đích (Destination). | Đích **lấy** dữ liệu từ nguồn. | Kiểm tra định kỳ xem nguồn có thay đổi không, sau đó Pull. |
| **Ví dụ** | Webhook, Event streaming. | Tải file từ Server về. | Cron job chạy mỗi 5 phút để kiểm tra Database. |

---

## 4. Batch Ingestion (Thu thập theo Lô)

Dùng khi xử lý dữ liệu hàng loạt, không cần real-time.

### Các mô hình Batch phổ biến

1.  **Snapshot vs Differential (Incremental):**
    *   **Snapshot:** Lấy toàn bộ dữ liệu hiện tại mỗi lần chạy. *Đơn giản nhưng tốn tài nguyên.*
    *   **Differential:** Chỉ lấy dữ liệu thay đổi từ lần chạy trước. *Hiệu quả, ít tốn băng thông.*

2.  **File-based Export:**
    *   Xuất dữ liệu ra file (CSV, JSON) rồi mới nạp.
    *   **Ưu điểm:** Tách biệt hệ nguồn và đích, an toàn hơn, cho phép xử lý sơ bộ (preprocess) trước khi nạp.

3.  **ETL vs ELT:**
    *   **ETL (Extract-Transform-Load):** Biến đổi trước khi nạp vào kho.
    *   **ELT (Extract-Load-Transform):** Nạp nguyên si vào kho (Data Lake/Warehouse) rồi mới biến đổi sau.

### Cân nhắc về kỹ thuật nạp (Insert/Update)
*   **Batch Size:** Không nên nạp từng dòng (Row-by-row) vào hệ thống Columnar (như BigQuery, Snowflake) vì sẽ tạo ra quá nhiều file nhỏ và chậm.
*   **Update Pattern:** Cập nhật từng dòng (Update in-place) rất chậm ở hệ thống phân tán. Ưu tiên ghi đè (Overwrite) hoặc Append.
*   **Data Migration:** Khi di chuyển database lớn, hãy dùng file trung gian (Intermediate file storage) và kiểm tra Schema kỹ trước khi di chuyển toàn bộ.

---

## 5. Push vs Pull Patterns

*   **Push:** Source gửi data đến Target. (Ví dụ: Webhook, Event streaming).
*   **Pull:** Target lấy data từ Source. (Ví dụ: Tải file từ Server).
*   **Polling:** Kiểm tra định kỳ xem Source có thay đổi không rồi Pull. (Ví dụ: Cron job).

## 6. Batch Ingestion Considerations

### Snapshot vs Differential Extraction
*   **Snapshot:** Lấy toàn bộ dữ liệu hiện tại mỗi lần chạy. Đơn giản nhưng tốn tài nguyên.
*   **Differential (Incremental):** Chỉ lấy dữ liệu thay đổi từ lần chạy trước. Hiệu quả, ít tốn băng thông.

### File-Based Export and Ingestion
*   **Ưu điểm:** Tách biệt hệ thống nguồn và đích. An toàn hơn (không cần mở port database trực tiếp). Cho phép xử lý sơ bộ (preprocess) trước khi nạp.
*   **Phương thức:** SFTP, SCP, Object Storage (S3).

### ETL vs ELT
*   **ETL (Extract-Transform-Load):** Biến đổi dữ liệu trước khi nạp vào kho. Phù hợp khi kho dữ liệu yêu cầu dữ liệu đã được làm sạch nghiêm ngặt.
*   **ELT (Extract-Load-Transform):** Nạp dữ liệu thô vào kho trước, sau đó mới biến đổi. Phù hợp với Data Lakehouse hiện đại (Snowflake, BigQuery, Databricks).

### Inserts, Updates, và Batch Size
*   **Vấn đề:** Chèn từng dòng (Row-by-row) vào hệ thống Columnar (như BigQuery, Snowflake) là cực kỳ chậm và tốn kém.
*   **Giải pháp:** Luôn gom thành Batch lớn (Bulk Insert/Load). Tránh cập nhật từng dòng (Update in-place) nếu có thể; thay vào đó nên ghi đè (Overwrite) hoặc Append dữ liệu mới.

### Data Migration
*   Di chuyển dữ liệu lớn (TB, PB) thường dùng file trung gian (Intermediate file storage).
*   Thách thức lớn nhất không phải là di chuyển dữ liệu, mà là cập nhật các kết nối **Pipeline** từ hệ thống cũ sang hệ thống mới.

---

## 7. Serialization and Deserialization (Mã hóa và Giải mã)

*   **Serialization:** Chuyển đổi cấu trúc dữ liệu thành định dạng để truyền tải hoặc lưu trữ (ví dụ: chuyển object Java thành JSON/Bytes).
*   **Deserialization:** Quá trình ngược lại (chuyển JSON/Bytes trở lại object).
*   **Cảnh báo:** Nếu định dạng nguồn (Serialization) không khớp với định dạng đích (Deserialization), dữ liệu sẽ bị "đóng băng" (không dùng được) hoặc lỗi nghiêm trọng.

---

## 8. Metadata (Siêu dữ liệu)

*   **Định nghĩa:** Dữ liệu mô tả về dữ liệu (Data about data).
*   **Tầm quan trọng:** Thiếu Metadata, Data Lake sẽ trở thành "Data Swamp" (Đầm lầy dữ liệu) - nơi chứa dữ liệu nhưng không ai dùng được.
*   **Nội dung:** Schema, nguồn gốc, thời gian tạo, loại dữ liệu... đều là Metadata.

---

Chào bạn, tôi là một chuyên gia Data Engineering. Dưới đây là bản dịch và tổng hợp nội dung bạn yêu cầu, được trình bày theo định dạng Markdown và phong cách "Decision Guide" để giúp bạn dễ dàng đưa ra quyết định kiến trúc.

***

# Kiến trúc Lưu trữ & Thu thập Dữ liệu Sự kiện (Event Data)

Chương này tập trung vào các nguyên tắc cơ bản của kiến trúc dữ liệu, vì **Storage (Lưu trữ)** là nền tảng quan trọng cho mọi hoạt động. Tuy nhiên, trước khi dữ liệu được lưu trữ, chúng ta phải xem xét cách thức **Ingestion (Thu thập)**.

Dưới đây là hướng dẫn ra quyết định cho các chiến lược thu thập và xử lý dữ liệu sự kiện.

## 1. Lựa chọn chiến lược Ingestion

Khi xử lý dữ liệu sự kiện (Event Data), bạn cần quyết định giữa việc thu thập theo lô (Batch) hoặc theo thời gian thực (Stream).

### Batch Ingestion
*   **Tại sao dùng?** Phù hợp cho các tác vụ không cần độ trễ tức thì, xử lý khối lượng lớn dữ liệu lịch sử, hoặc khi chi phí tài nguyên cần được tối ưu hóa.
*   **Khi nào dùng?** Khi dữ liệu có thể chờ đợi (ví dụ: phân tích cuối ngày) và nguồn dữ liệu không liên tục phát sinh.
*   **Ưu điểm:** Dễ quản lý, chi phí xử lý thấp hơn, đơn giản hóa việc xử lý lỗi.
*   **Nhược điểm:** Độ trễ cao (Latency), không phù hợp cho các hệ thống cảnh báo thời gian thực.

### Message and Stream Ingestion (Thu thập Tin nhắn & Luồng)
*   **Tại sao dùng?** Để xử lý dữ liệu ngay khi nó được tạo ra, cần độ trễ thấp và khả năng phản hồi tức thì.
*   **Khi nào dùng?** Khi dữ liệu đến liên tục (như log máy chủ, cảm biến IoT, giao dịch tài chính) và hệ thống cần phản ứng ngay lập tức.
*   **Ưu điểm:** Độ trễ thấp, khả năng mở rộng cao, xử lý được luồng dữ liệu vô tận.
*   **Nhược điểm:** Phức tạp hơn trong việc xử lý lỗi và bảo trì, chi phí vận hành có thể cao hơn.

---

## 2. Các yếu tố then chốt khi xử lý Dữ liệu Sự kiện

Khi thu thập dữ liệu sự kiện (dựa trên nội dung Chapters 5 & 6), bạn cần chú ý 3 vấn đề lớn sau:

### A. Schema Evolution (Tiến hóa Schema)

Đây là hiện tượng các trường dữ liệu được thêm/bớt hoặc kiểu dữ liệu thay đổi (ví dụ: từ `string` sang `integer`).

*   **Vấn đề:** Các thay đổi này có thể làm hỏng **Data Pipeline** hoặc điểm đến (Destination) nếu không được xử lý đúng cách. Ví dụ: một bản cập nhật firmware IoT thêm trường mới, hoặc API của bên thứ ba thay đổi cấu trúc payload.
*   **Hướng dẫn ra quyết định & Giải pháp:**

| Giải pháp | Khi nào dùng? | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- | :--- |
| **Schema Registry** | Luôn luôn dùng nếu hệ thống hỗ trợ. | Giúp version hóa schema, quản lý các thay đổi một cách có hệ thống. | Yêu cầu framework xử lý dữ liệu phải hỗ trợ tích hợp sẵn. |
| **Dead-Letter Queue (DLQ)** | Khi cần xử lý lỗi và điều tra các sự kiện bị từ chối. | Giúp tách các sự kiện lỗi ra để phân tích mà không làm gián đoạn luồng chính. | Cần thêm dung lượng lưu trữ và logic xử lý riêng cho DLQ. |
| **Trao đổi trước (Communication)** | Luôn luôn nên làm. | Hiệu quả nhất, tránh được các lỗi vỡ (breaking changes) từ phía nguồn. | Phụ thuộc vào quy trình phối hợp giữa các team (Upstream/Downstream). |

### B. Late-Arriving Data (Dữ liệu đến trễ)

*   **Tại sao dùng? (Xử lý như thế nào):** Bạn cần nhận biết rằng dữ liệu có thể đến muộn so với thời gian thực tế nó xảy ra (do latency mạng, lỗi thiết bị...).
*   **Khi nào dùng?** Khi bạn cần báo cáo dựa trên **Event Time** (thời gian sự kiện xảy ra) thay vì **Ingestion Time** (thời gian dữ liệu được thu thập).
*   **Quyết định quan trọng:** Bạn phải thiết lập một **Cutoff time (Thời gian cắt)**. Nếu dữ liệu đến sau khoảng thời gian này, nó sẽ bị từ chối hoặc xử lý riêng để đảm bảo tính toàn vẹn của báo cáo.

### C. Ordering and Multiple Delivery (Thứ tự và Giao nhận nhiều lần)

*   **Tại sao dùng?** Đảm bảo dữ liệu được xử lý đúng trình tự và không bị trùng lặp.
*   **Khi nào dùng?** Trong các hệ thống Stream (như Kafka), thứ tự tin nhắn có thể bị乱序 (xáo trộn) và một tin nhắn có thể được giao nhận nhiều lần do cơ chế đảm bảo độ tin cậy (At-least-once delivery).
*   **Ưu nhược điểm:**
    *   **Ưu điểm của việc xử lý Ordering:** Đảm bảo tính chính xác của các giao dịch (ví dụ: số dư tài khoản).
    *   **Nhược điểm:** Việc đảm bảo thứ tự tuyệt đối (Strict Ordering) thường làm giảm thông lượng (Throughput) và độ phức tạp của hệ thống tăng cao.

---

**Tóm lại:** Khi thiết kế Data Pipeline cho dữ liệu sự kiện, hãy ưu tiên sử dụng **Schema Registry** để quản lý thay đổi, thiết lập quy tắc xử lý **Late-arriving data** rõ ràng, và luôn chuẩn bị tinh thần cho việc dữ liệu đến không đúng thứ tự hoặc bị lặp lại.

---

