# Chapter 5 for more details.

Dưới đây là bản dịch và tổng hợp nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide** (Hướng dẫn ra quyết định) tập trung vào các yếu tố then chốt của việc Ingestion (Thu thập dữ liệu).

---

# Quyết Định Khi Xây Dựng Hệ Thống Thu Thập Dữ Liệu (Data Ingestion)

Tài liệu này tổng hợp các yếu tố quan trọng trong việc thiết kế pipeline thu thập dữ liệu, bao gồm xử lý luồng (streaming), cơ chế truy vấn, xử lý lỗi và lựa chọn công nghệ.

## 1. Kiến Trúc Streaming & Lỗi

### Replay (Phát lại)
**Tại sao dùng?**
Cho phép hệ thống "lùi thời gian" để lấy lại dữ liệu trong quá khứ. Đây là tính năng quan trọng khi bạn cần xử lý lại (reprocess) dữ liệu do lỗi logic hoặc cập nhật model.

**Khi nào dùng?**
*   Khi cần sửa lỗi và xử lý lại dữ liệu của một khoảng thời gian cụ thể.
*   Các nền tảng như **Kafka**, **Kinesis**, và **Pub/Sub** hỗ trợ tính năng này. Lưu ý: **RabbitMQ** thường xóa tin nhắn sau khi đã đọc, nên không hỗ trợ replay.

### Time to Live (TTL)
**Tại sao dùng?**
Quản lý vòng đời của dữ liệu, ngăn chặn việc lưu trữ quá nhiều dữ liệu chưa xử lý (backlog) và giảm áp lực lên hệ thống (backpressure).

**Ưu nhược điểm & Cân bằng:**
*   **TTL quá ngắn (mili-giây/giây):** Rủi ro mất dữ liệu trước khi kịp xử lý.
*   **TTL quá dài (tuần/tháng):** Tạo ra backlog lớn, gây trễ hệ thống.
*   **Lựa chọn nền tảng:**
    *   *Google Cloud Pub/Sub:* Tối đa 7 ngày.
    *   *Amazon Kinesis:* Tối đa 365 ngày.
    *   *Kafka:* Không giới hạn (phụ thuộc dung lượng disk) hoặc lưu trữ lên cloud object storage.

### Message Size (Kích thước thông điệp)
**Cân bằng:**
Bạn phải đảm bảo hệ thống xử lý được kích thước tối đa của tin nhắn.
*   **Kinesis:** Giới hạn 1MB.
*   **Kafka:** Mặc định 1MB, có thể cấu hình lên tới 20MB+.

### Error Handling & Dead-Letter Queues (DLQ)
**Tại sao dùng?**
Xử lý các sự kiện lỗi (tin nhắn quá lớn, hết hạn TTL, topic không tồn tại) mà không làm tắc nghẽn pipeline chính.

**Quy trình:**
*   Các sự kiện "tốt" được chuyển đến Consumer.
*   Các sự kiện "lỗi" được chuyển vào DLQ để phân tích và xử lý sau.

### Consumer Pull vs Push
**So sánh:**

| Phương thức | Mô tả | Ví dụ nền tảng | Ưu điểm |
| :--- | :--- | :--- | :--- |
| **Pull** | Consumer chủ động đọc và xác nhận (ack) sau khi xử lý. | Kafka, Kinesis | Kiểm soát tốt tốc độ xử lý, phù hợp với đa số ứng dụng Data Engineering. |
| **Push** | Hệ thống chủ động gửi dữ liệu đến listener/consumer. | Pub/Sub, RabbitMQ | Phù hợp ứng dụng chuyên biệt cần phản hồi tức thì. |

---

## 2. Các Phương Pháp Thu Thập Dữ Liệu (Ways to Ingest Data)

### Direct Database Connection (Kết nối trực tiếp)
Sử dụng **ODBC** hoặc **JDBC** để truy vấn và đọc dữ liệu qua mạng.

**So sánh ODBC vs JDBC:**

| Tiêu chí | ODBC | JDBC |
| :--- | :--- | :--- |
| **Ngôn ngữ** | Đa ngôn ngữ (C/C++...). | Chuyên cho Java (nhưng có thể dùng qua wrapper cho Python, Scala...). |
| **Cấu trúc** | Native binary theo OS/Architecture. | Một driver duy nhất chạy trên JVM (portable). |
| **Hạn chế** | Khó xử lý dữ liệu lồng ghép (nested), phải serialize lại thành hàng (rows). | Tương tự ODBC về giới hạn cấu trúc dữ liệu. |

**Lưu ý:** Các phương pháp này gây tải nặng lên nguồn dữ liệu. Nên dùng song song với các công nghệ khác (ví dụ: ghi vào Object Storage trước).

### Change Data Capture (CDC)
Quá trình thu thập các thay đổi từ cơ sở dữ liệu nguồn.

**1. Batch-oriented CDC (CDC theo batch):**
*   **Cách hoạt động:** Dựa trên cột `updated_at` để truy vấn các bản ghi thay đổi trong một khoảng thời gian.
*   **Hạn chế:** Nếu một bản ghi thay đổi nhiều lần trong khoảng thời gian đó, bạn chỉ nhận được bản cuối cùng (ví dụ: số dư tài khoản cuối ngày, mất các giao dịch ở giữa).
*   **Giải pháp:** Dùng schema "Insert-Only" (chỉ chèn mới, không cập nhật).

**2. Continuous CDC (CDC liên tục):**
*   **Cách hoạt động:** Đọc log nhị phân (binary log) của database (ví dụ: Debezium + PostgreSQL) hoặc dùng tính năng có sẵn của cloud DB để kích hoạt event stream.
*   **Ưu điểm:** Thu thập đầy đủ history, hỗ trợ real-time.

**3. CDC vs Database Replication:**

| Loại | Đặc điểm | Phù hợp khi |
| :--- | :--- | :--- |
| **Synchronous Replication** | Đồng bộ chặt chẽ giữa Primary và Replica. Replica phải cùng loại DB. | Cần đảm bảo dữ liệu tuyệt đối chính xác ngay lập tức, dùng Read Replica để offload read query. |
| **Asynchronous CDC** | Lỏng lẻo, có thể có độ trễ. Có thể gửi đến nhiều đích (Object Storage, Streaming...). | Phân tích dữ liệu (Analytics), không cần đồng bộ tức thì, cần kiến trúc linh hoạt. |

**Cân nhắc:** CDC tốn tài nguyên CPU, Disk, Network. Cần test kỹ trước khi bật trên hệ thống Production.

### APIs
**Tình trạng hiện tại:**
*   Không có tiêu chuẩn chung cho việc trao đổi dữ liệu qua API.
*   Việc xây dựng và bảo trì connector thủ công tốn rất nhiều thời gian.

**Giải pháp & Quyết định:**
1.  **Data Sharing:** Nếu có thể, hãy dùng nền tảng chia sẻ dữ liệu (BigQuery, Snowflake, S3) thay vì gọi API.
2.  **Managed Connectors:** Sử dụng dịch vụ của第三方 (SaaS) để xử lý việc kết nối thay vì tự làm (xem phần Managed Data Connectors bên dưới).
3.  **Custom API:** Chỉ nên làm thủ công nếu API đó thực sự đặc thù và không có công cụ hỗ trợ.

### Message Queues & Event-Streaming Platforms
Dùng cho dữ liệu real-time từ web, mobile, IoT.

**So sánh Message vs Stream:**

| Thuộc tính | Message Queue | Event Stream |
| :--- | :--- | :--- |
| **Bản chất** | Xử lý ở mức event đơn lẻ. | Dạng log có thứ tự (Ordered Log). |
| **Tính chất** | Tạm thời (Transient). Sau khi đọc sẽ bị xóa (ack & remove). | Vĩnh viễn (theo TTL). Có thể replay, query theo khoảng thời gian. |
| **Biến đổi** | Đơn giản (Publish -> Consume). | Phức tạp (Publish -> Consume -> Republish -> Reconsume). |

**Lưu ý thiết kế:**
*   Streaming là phi tuyến tính (non-linear), dữ liệu có thể được tái sử dụng nhiều lần.
*   Cần đảm bảo băng thông (partition/shard) và tài nguyên (CPU/RAM) đủ để xử lý peak load. Nên dùng **Managed Services** để giảm bớt gánh nặng vận hành.

---

## 3. Các Công Cụ & Phương Thức Hỗ Trợ

### Managed Data Connectors (Bộ kết nối được quản lý)
**Tại sao dùng?**
Thay vì tự viết code kết nối database/API, hãy dùng dịch vụ quản lý.

**Lợi ích:**
*   Có sẵn hàng trăm connector (SaaS, OSS).
*   Xử lý việc đồng bộ hóa, lên lịch, và cảnh báo lỗi tự động.
*   Tiết kiệm thời gian phát triển và bảo trì (Undifferentiated heavy lifting).

### Moving Data with Object Storage (Object Storage)
Là phương thức tối ưu để trao đổi file trong cloud.
*   **Ưu điểm:** An toàn, dung lượng lớn, chuẩn bảo mật mới, hỗ trợ truy cập tạm thời (Signed URL).
*   **Công dụng:** Di chuyển dữ liệu giữa Data Lake, các team, hoặc tổ chức.

### EDI (Electronic Data Interpretation)
**Tình huống:**
Là các phương thức cũ (email, USB, file dump) do hệ thống IT cũ hoặc quy trình thủ công.

**Giải pháp:**
Tự động hóa bằng cách dùng Email Server cloud để nhận file và tự động kích hoạt pipeline xử lý (Orchestration), tránh tải thủ công.

### File Export từ Database
*   **Vấn đề:** Export dữ liệu lớn (Full scan) gây tải nặng lên database giao dịch (Transactional DB).
*   **Giải pháp:** Chia nhỏ các truy vấn export (Query partitioning) hoặc chạy vào thời gian thấp điểm (Off-hours).

---

Chào bạn, tôi là chuyên gia Data Engineering. Dưới đây là bản dịch và tổng hợp nội dung bạn cung cấp theo định dạng "Decision Guide" như yêu cầu.

***

# Các Phương pháp và Cân nhắc về Data Ingestion

Tài liệu này cung cấp hướng dẫn ra quyết định cho các kỹ sư dữ liệu khi lựa chọn phương pháp và công cụ để đưa dữ liệu (Ingestion) vào hệ thống. Nội dung tập trung vào việc đánh giá các lựa chọn dựa trên bối cảnh sử dụng, ưu nhược điểm và tác động đến toàn bộ vòng đời kỹ thuật dữ liệu.

## 1. Xuất dữ liệu từ Warehouse và Optimizations

### Khi nào cần tối ưu hóa?
Khi tần suất xuất dữ liệu từ Data Warehouse (như Snowflake, BigQuery, Redshift) cao và trùng với thời điểm nguồn hệ thống (Source System) chịu tải nặng.

### Các lựa chọn và quyết định:
*   **Đọc theo Partition/Ranges:** Thay vì quét toàn bộ, hãy đọc dữ liệu theo từng phân vùng hoặc khoảng thời gian cụ thể để giảm tải.
*   **Sử dụng Read Replica:** Nếu các tác vụ xuất dữ liệu (exports) diễn ra nhiều lần trong ngày và ảnh hưởng đến hiệu năng hệ thống nguồn, hãy chuyển hướng các truy vấn đọc sang Read Replica.
*   **Direct Export:** Các Warehouse đám mây hiện đại đều được tối ưu hóa để xuất trực tiếp ra Object Storage (như S3) ở nhiều định dạng khác nhau.

## 2. Lựa chọn Định dạng File (File Formats)

### Tại sao cần quan tâm định dạng file?
Định dạng file quyết định độ tin cậy, hiệu suất và khả năng xử lý cấu trúc dữ liệu phức tạp trong quá trình Ingestion.

### So sánh định dạng:

| Tiêu chí | CSV | Parquet, Avro, Arrow, ORC, JSON |
| :--- | :--- | :--- |
| **Định dạng** | Văn bản thuần túy, không chuẩn hóa统一. | Nén nhị phân, có cấu trúc. |
| **Schema** | Không tự mã hóa schema. Phải cấu hình thủ công ở hệ thống đích. | Tự động mã hóa schema. |
| **Xử lý chuỗi & Lồng ghép (Nested)** | Dễ lỗi với ký tự phân tách (delimiter). Không hỗ trợ cấu trúc lồng ghép tự nhiên. | Xử lý chuỗi phức tạp và cấu trúc lồng ghép (nested data) một cách tự nhiên. |
| **Hiệu suất** | Thấp, đặc biệt với Columnar Database. | **Cao**. Cho phép chuyển đổi định dạng trực tiếp giữa các cột (transcoding). Tối ưu cho Query Engine. Arrow đặc biệt hiệu quả trong môi trường Data Lake (map trực tiếp vào bộ nhớ). |
| **Hạn chế** | **Rủi ro lỗi cao**. Dễ gây lỗi khi dữ liệu chứa dấu phẩy hoặc ký tự đặc biệt. | Không phải hệ thống nguồn nào cũng hỗ trợ sẵn. |

### Quyết định:
*   **Tránh dùng CSV trong Production:** Nếu bắt buộc dùng CSV, phải ghi rõ thông tin encoding và schema vào metadata.
*   **Ưu tiên định dạng nhị phân (Parquet/Arrow):** Khi cần hiệu suất cao, xử lý nested data và tích hợp với Data Lake/Columnar Warehouse.

## 3. Công cụ và Giao thức Ingestion

### A. Shell Scripting
*   **Khi nào dùng?** Khi cần tự động hóa các tác vụ phức tạp: đọc từ DB -> chuyển đổi định dạng -> upload lên Object Storage -> kích hoạt Ingestion process. Phù hợp với nguồn dữ liệu nhỏ hoặc quy trình chưa cần quy mô lớn.
*   **Ưu điểm:** Linh hoạt, có thể scripting cho bất kỳ công cụ nào.
*   **Nhược điểm:** Khó scale trên một instance đơn lẻ. Khi quy trình phức tạp và SLA nghiêm ngặt, cần chuyển sang Orchestration system.

### B. SSH (Secure Shell)
*   **Vai trò:** Là giao thức bảo mật, **không phải** là chiến lược Ingestion trực tiếp.
*   **Cách dùng:**
    1.  **File Transfer:** Dùng SCP (Secure Copy).
    2.  **Kết nối Database An toàn:** Sử dụng **SSH Tunnel** qua Bastion Host (máy trung gian) để kết nối tới Database nội bộ mà không cần expose trực tiếp lên Internet.

### C. SFTP & SCP
*   **Khi nào dùng?** Khi làm việc với đối tác doanh nghiệp (B2B) yêu cầu trao đổi dữ liệu qua các giao thức này.
*   **Lưu ý:** Dù SFTP/SCP là thực tế phổ biến, cần thực hiện phân tích bảo mật nghiêm ngặt (Defense in depth) để tránh rò rỉ dữ liệu.

### D. Webhooks (Reverse API)
*   **Cơ chế:** Thay vì bạn gọi API (Pull), nhà cung cấp dữ liệu sẽ gọi API của bạn (Push) để gửi dữ liệu.
*   **Cấu trúc điển hình (AWS Example):**
    *   **Ingestion:** Lambda (Nhận sự kiện) -> Kinesis (Buffer/Tích lũy) -> Flink (Xử lý thời gian thực) -> S3 (Lưu trữ dài hạn).
*   **Quyết định:**
    *   **Nhược điểm:** Kiến trúc Webhook thường phức tạp, dễ vỡ (brittle), khó bảo trì và dính liền với các giai đoạn khác (Storage, Processing).
    *   **Giải pháp:** Sử dụng các công cụ off-the-shelf (như Lambda, Kinesis) để xây dựng kiến trúc robust hơn thay vì tự code thủ công.

### E. Web Interface & Web Scraping
*   **Web Interface (Manual):** Chỉ dùng khi không còn lựa chọn nào khác (API/FTP không khả dụng). Nhược điểm lớn là thiếu tự động hóa và phụ thuộc vào con người.
*   **Web Scraping:**
    *   **Cân nhắc Đạo đức & Pháp lý:** Luôn kiểm tra Terms of Service. Tránh gây tấn công DoS (từ chối dịch vụ) hoặc làm sập server mục tiêu.
    *   **Kỹ thuật:** HTML thay đổi liên tục làm hệ thống dễ hỏng (fragile).
    *   **Quyết định:** Cần cân nhắc liệu việc duy trì hệ thống Scraping có xứng đáng với công sức bỏ ra hay không.

### F. Transfer Appliances (Thiết bị chuyển vật lý)
*   **Khi nào dùng?** Khi khối lượng dữ liệu cực lớn (**> 100TB - Petabytes**).
*   **Tại sao dùng?** Chuyển qua Internet quá chậm và chi phí Data Egress rất cao.
*   **Ví dụ:** AWS Snowball, Snowmobile (chuyển cả thùng chứa).
*   **Lưu ý:** Đây là giải pháp cho **một lần** (One-time migration), không phù hợp cho luồng dữ liệu liên tục (ongoing workloads).

### G. Data Sharing (Chia sẻ dữ liệu)
*   **Bản chất:** Đây không phải là Ingestion theo nghĩa sở hữu dữ liệu vật lý (Physical possession). Bạn chỉ có quyền truy cập đọc (Read-only).
*   **Lợi ích:** Phổ biến trên các Cloud Platform (Data Marketplace), cho phép tích hợp dữ liệu của bên thứ ba mà không cần qua bước Ingestion thủ công.

## 4. Lời khuyên cho Kỹ sư Dữ liệu (Data Engineers)

### Làm việc với các bên liên quan (Stakeholders)
Data Ingestion nằm ở giao điểm của nhiều bộ phận. Bạn cần phối hợp với:
1.  **Upstream (Người tạo dữ liệu - Software Engineers):** Họ thường coi Data Engineers là người tiêu thụ dữ liệu thô (data exhaust).
2.  **Downstream (Người dùng dữ liệu - Consumers):** Các nhóm phân tích, khoa học dữ liệu.

### Chiến lược:
*   **Thay đổi tư duy:** Đừng chỉ là người "dọn dẹp" dữ liệu. Hãy mời các Software Engineers trở thành **stakeholder** trong kết quả kỹ thuật dữ liệu.
*   **Cơ hội:** Đây là cách để cải thiện chất lượng dữ liệu ngay từ nguồn (source) và phá vỡ các silo tổ chức.

---

