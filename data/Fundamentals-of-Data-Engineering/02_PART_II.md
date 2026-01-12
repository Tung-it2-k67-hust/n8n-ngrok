# PART II

Dưới đây là bản dịch và tổng hợp nội dung từ chương "Data Generation in Source Systems" sang tiếng Việt, được trình bày theo phong cách Decision Guide dành cho kỹ sư Data Engineering.

***

# CHƯƠNG 5: Tạo dữ liệu trong Hệ thống nguồn (Data Generation in Source Systems)

Chào mừng bạn đến với giai đoạn đầu tiên của vòng đời kỹ thuật dữ liệu: **Data Generation** (tạo dữ liệu) trong các hệ thống nguồn. Công việc của một kỹ sư dữ liệu là lấy dữ liệu từ các hệ thống nguồn, xử lý và biến nó thành thông tin hữu ích cho các trường hợp sử dụng下游 (downstream use cases). Tuy nhiên, trước khi có thể lấy được dữ liệu thô, bạn phải hiểu dữ liệu tồn tại ở đâu, cách nó được tạo ra以及 các đặc điểm và "tật" của nó.

Chương này tập trung vào các mô hình hệ thống nguồn hoạt động phổ biến và các loại hệ thống nguồn chính. Chúng ta sẽ xem xét dữ liệu mà các hệ thống này tạo ra và những điều cần cân nhắc khi làm việc với chúng.

## 1. Nguồn gốc Dữ liệu: Dữ liệu được tạo ra như thế nào?

Dữ liệu là một tập hợp các sự thật và con số chưa được tổ chức. Dữ liệu được tạo ra theo 2 cách:

*   **Dữ liệu Analog (Tương tự):** Tồn tại trong thế giới thực (giọng nói, chữ viết tay). Dữ liệu này thường không kéo dài (transient).
*   **Dữ liệu Kỹ thuật số (Digital):** Chuyển đổi từ Analog sang Digital (ví dụ: Voice-to-Text) hoặc là sản phẩm gốc của hệ thống kỹ thuật số (ví dụ: giao dịch thẻ tín dụng).

> **Lời khuyên:** Hãy làm quen với hệ thống nguồn của bạn. Đọc tài liệu để hiểu cách nó hoạt động (viết, commit, query...) và các đặc điểm có thể ảnh hưởng đến việc **Ingestion** (nuốt dữ liệu).

---

## 2. Các ý tưởng chính về Hệ thống nguồn (Source Systems)

Khi làm việc với Source Systems, bạn sẽ thường xuyên gặp phải các khái niệm sau:

### A. Files và Dữ liệu Phi cấu trúc (Unstructured Data)
*   **Là gì?** Dữ liệu được lưu trữ dưới dạng file (Excel, CSV, TXT, JSON, XML).
*   **Tại sao dùng?** Là phương tiện trao đổi dữ liệu phổ biến, đặc biệt khi làm việc với các cơ quan chính phủ hoặc đối tác bên thứ ba.
*   **Khi nào dùng?** Khi bạn nhận dữ liệu thủ công hoặc đầu ra từ quy trình hệ thống nguồn.
*   **Ưu nhược điểm:**
    *   *Ưu:* Dễ dàng chia sẻ, phổ biến.
    *   *Nhược:* Có thể có "tật" (quirks), cấu trúc lỏng lẻo (có thể là structured, semistructured hoặc unstructured), gây khó khăn cho việc xử lý tự động.

### B. APIs (Application Programming Interfaces)
*   **Là gì?** Cách tiêu chuẩn để trao đổi dữ liệu giữa các hệ thống.
*   **Tại sao dùng?** Lý tưởng để lấy dữ liệu một cách có chương trình (programmatically).
*   **Khi nào dùng?** Khi hệ thống nguồn cung cấp API RESTful hoặc GraphQL.
*   **Ưu nhược điểm:**
    *   *Ưu:* Tiêu chuẩn hóa, kiểm soát truy cập tốt.
    *   *Nhược:* Trong thực tế, nhiều API vẫn bộc lộ sự phức tạp của dữ liệu. Việc duy trì các kết nối API tùy chỉnh (custom) đòi hỏi nhiều công sức.

### C. Cơ sở dữ liệu Ứng dụng (Application Databases - OLTP)
*   **Là gì?** Database lưu trữ trạng thái của ứng dụng (ví dụ: số dư ngân hàng).
*   **Loại hệ thống:** **OLTP (Online Transaction Processing)**.
*   **Tại sao dùng?** Để xử lý các giao dịch riêng lẻ với tốc độ cao và độ trễ thấp.
*   **Khi nào dùng?** Khi có hàng nghìn hoặc hàng triệu người dùng tương tác đồng thời (cập nhật, ghi dữ liệu).
*   **Ưu nhược điểm:**
    *   *Ưu:* Tốc độ nhanh cho các truy vấn đọc/ghi đơn lẻ, hỗ trợ **ACID**.
    *   *Nhược:* Kém hiệu quả khi xử lý các truy vấn phân tích quy mô lớn (scan lượng dữ liệu khổng lồ).

#### Bảng so sánh: OLTP vs OLAP

| Đặc điểm | OLTP (Transaction) | OLAP (Analytical) |
| :--- | :--- | :--- |
| **Mục đích** | Xử lý giao dịch nghiệp vụ hàng ngày | Phân tích, báo cáo, khám phá dữ liệu |
| **Tốc độ** | Rất nhanh (đơn truy vấn) | Chậm hơn (cần scan nhiều dữ liệu) |
| **Loại truy vấn** | Đọc/Ghi (Read/Write) | Chủ yếu là Đọc (Read-only) |
| **Quy mô dữ liệu** | Hàng triệu record, nhưng truy vấn nhỏ | Hàng tỷ record, truy vấn phức tạp |
| **Ví dụ** | MySQL, PostgreSQL | Snowflake, BigQuery, Redshift |

---

## 3. Các khái niệm chuyên sâu

### A. ACID và Atomic Transactions
*   **ACID là gì?** Một tập hợp các đặc tính đảm bảo tính toàn vẹn của dữ liệu:
    *   **A**tomicity (Tính nguyên tử): Giao dịch thành công 100% hoặc thất bại hoàn toàn (không bỏ dở).
    *   **C**onsistency (Tính nhất quán): Dữ liệu luôn tuân thủ các quy tắc.
    *   **I**solation (Tính cô lập): Các giao dịch không làm ảnh hưởng lẫn nhau.
    *   **D**urability (Tính bền vững): Dữ liệu đã ghi sẽ không bị mất dù mất điện.
*   **Atomic Transaction (Giao dịch nguyên tử):** Ví dụ chuyển tiền từ tài khoản A sang B. Toàn bộ quá trình phải thành công (A trừ tiền, B cộng tiền) hoặc thất bại (không thay đổi gì).
*   **Quyết định:** Bạn có cần đảm bảo dữ liệu tuyệt đối chính xác không? Nếu có, cần hệ thống hỗ trợ ACID. Nếu cần tốc độ và sẵng sàng chấp nhận dữ liệu không nhất quán tạm thời (Eventual Consistency), hãy cân nhắc các hệ thống NoSQL.

### B. Change Data Capture (CDC)
*   **Là gì?** Phương pháp trích xuất mỗi thay đổi (insert, update, delete) xảy ra trong database.
*   **Tại sao dùng?** Để sao chép dữ liệu gần thời gian thực (near real-time) hoặc tạo luồng sự kiện (event stream).
*   **Khi nào dùng?** Khi cần đồng bộ dữ liệu từ OLTP sang Data Warehouse hoặc Data Lake mà không ảnh hưởng đến performance của hệ thống nguồn.

### C. Logs (Nhật ký)
*   **Là gì?** Ghi lại thông tin về các sự kiện xảy ra trong hệ thống (OS, App, Server, IoT).
*   **Thành phần bắt buộc:** Phải ghi rõ **Ai (Who)**, **Cái gì (What)**, **Khi nào (When)**.
*   **Phân loại Log:**
    1.  **Binary-encoded logs:** Hiệu suất cao, tiết kiệm dung lượng (ví dụ: Database Write-ahead Logs).
    2.  **Semistructured logs (JSON):** Dễ đọc máy, phổ biến nhưng kém hiệu quả hơn Binary.
    3.  **Plain-text logs:** Dữ liệu thô từ console output, khó trích xuất thông tin tự động.

#### Database Logs (Quan trọng)
*   **Write-ahead Logs (WAL):** Là binary files, ghi lại các thao tác trước khi ghi vào database chính.
*   **Vai trò:** Đảm bảo khả năng phục hồi (recoverability) sau sự cố và là nguồn dữ liệu chính cho **CDC**.

### D. CRUD
*   **Là gì?** Mô hình giao dịch cơ bản: **C**reate (Tạo), **R**ead (Đọc), **U**pdate (Cập nhật), **D**elete (Xóa).
*   **Nguyên tắc:** Dữ liệu phải được tạo (Create) trước khi được sử dụng.

---

## Tóm tắt Decision Guide cho Kỹ sư Dữ liệu

| Nguồn dữ liệu | Khi nào lựa chọn? | Cân nhắc chính |
| :--- | :--- | :--- |
| **Files (Excel, CSV, JSON)** | Khi nhận dữ liệu từ đối tác, API không khả dụng hoặc dữ liệu thủ công. | Cần xử lý "tật" của file, xử lý encoding và schema evolution. |
| **APIs** | Khi cần tích hợp với SaaS hoặc hệ thống hiện代. | Cần quản lý rate limit, authentication và duy trì kết nối custom. |
| **OLTP Databases** | Khi cần dữ liệu giao dịch thời gian thực (Real-time). | Tránh chạy truy vấn phân tích nặng trực tiếp lên OLTP để không gây nghẽn hệ thống nghiệp vụ. Sử dụng CDC để lấy dữ liệu ra ngoài. |
| **Logs** | Khi cần ghi lại hành trình hệ thống, debug hoặc phân tích hành vi người dùng. | Cần phân biệt Log level (lỗi hay info) và độ trễ log (Batch hay Real-time). Database Logs là nguồn vàng cho CDC. |

---

Dưới đây là bản dịch và tổng hợp nội dung từ chương "PART II" của sách, được trình bày theo phong cách **Decision Guide** dành cho chuyên gia Data Engineering.

***

# Nguồn Dữ Liệu (Source Systems) và Kiến Trúc Dữ Liệu

Tài liệu này tập trung vào các mô hình dữ liệu, kiến trúc tin nhắn và cơ sở dữ liệu mà một Kỹ sư Dữ liệu (Data Engineer) thường gặp phải khi xây dựng Data Pipeline.

## 1. Mô hình xử lý dữ liệu: CRUD vs Insert-Only

Khi thiết kế Data Pipeline, việc hiểu cách dữ liệu được tạo và thay đổi trong hệ thống nguồn là bước đầu tiên để lựa chọn phương pháp Ingestion phù hợp.

### Mô hình CRUD (Create, Read, Update, Delete)

Đây là mô hình chuẩn trong các ứng dụng phần mềm, API và cơ sở dữ liệu quan hệ.

*   **Tại sao dùng?** Đảm bảo tính toàn vẹn của dữ liệu và trạng thái hiện tại (Current State). Phù hợp cho các hệ thống giao dịch (OLTP) cần độ chính xác cao.
*   **Khi nào dùng?** Khi bạn chỉ quan tâm đến dữ liệu ở thời điểm hiện tại và không cần lịch sử thay đổi.
*   **Ưu điểm:** Dữ liệu gọn gàng, mỗi bản ghi chỉ chứa thông tin mới nhất.
*   **Nhược điểm:** Khó lấy lịch sử thay đổi (History). Nếu dùng Snapshot (truy vấn định kỳ), bạn sẽ mất dữ liệu giữa các lần truy vấn. Cần áp dụng CDC (Change Data Capture) để ghi lại lịch sử.

### Mô hình Insert-Only (Chỉ chèn)

Thay vì cập nhật bản ghi cũ, hệ thống sẽ chèn bản ghi mới với timestamp.

*   **Tại sao dùng?** Để lưu trữ toàn bộ lịch sử thay đổi ngay trong bảng dữ liệu. Rất hữu ích cho các ứng dụng cần xem lại lịch sử (ví dụ: lịch sử địa chỉ khách hàng).
*   **Khi nào dùng?** Khi dữ liệu thay đổi thường xuyên và bạn cần track history mà không muốn dùng đến Log hệ thống.
*   **Ưu điểm:** Giữ lại được toàn bộ dòng thời gian (Time-series data) dễ dàng.
*   **Nhược điểm:**
    *   **Dung lượng:** Bảng dữ liệu tăng trưởng rất nhanh (bloat).
    *   **Hiệu năng truy vấn:** Để lấy dữ liệu mới nhất (Current State), cần thực hiện truy vấn phức tạp (ví dụ: `MAX(created_timestamp)`), tốn tài nguyên nếu số lượng bản ghi lớn.

---

## 2. Kiến trúc Tin nhắn: Message Queue vs Streaming Platform

Hai khái niệm này thường bị nhầm lẫn nhưng có sự khác biệt cốt lõi ảnh hưởng đến thiết kế Data Pipeline.

### Message Queue (Hàng đợi tin nhắn)

*   **Bản chất:** Gửi tin nhắn rời rạc (discrete signals) từ Publisher đến Consumer. Tin nhắn sau khi được xử lý sẽ bị xóa khỏi hàng đợi.
*   **Tại sao dùng?** Để giao tiếp giữa các service (microservices) hoặc xử lý tác vụ bất đồng bộ.
*   **Khi nào dùng?** Khi bạn cần xử lý từng sự kiện riêng lẻ và không quan tâm đến thứ tự tuyệt đối hoặc lưu trữ lâu dài.
*   **Ví dụ:** IoT gửi nhiệt độ -> Service quyết định bật/tắt lò sưởi -> Gửi lệnh điều khiển. Xong là xóa tin nhắn.

### Streaming Platform (Nền tảng luồng dữ liệu)

*   **Bản chất:** Là một log append-only (nhật ký chỉ chèn) của các sự kiện, được lưu trữ và sắp xếp theo thứ tự (thường dùng timestamp hoặc ID).
*   **Tại sao dùng?** Khi bạn quan tâm đến **xu hướng** và **tổng hợp** của nhiều sự kiện theo thời gian.
*   **Khi nào dùng?** Khi cần phân tích phức tạp, replay lại dữ liệu (quay lui thời điểm), hoặc xử lý dữ liệu theo luồng liên tục.
*   **Ưu điểm:** Dữ liệu được lưu trữ lâu dài (tuần/tháng), cho phép thực hiện các phép toán phức tạp (aggregations) và phân tích lịch sử.

---

## 3. Quản lý Thời gian trong Data Pipeline

Trong môi trường Streaming, thời gian là yếu tố sống còn. Có 4 loại thời gian cần ghi lại trong quy trình ETL/ELT:

| Loại Thời gian | Định nghĩa | Tầm quan trọng |
| :--- | :--- | :--- |
| **Event Time** | Thời điểm sự kiện được tạo ra tại nguồn (ví dụ: lúc khách hàng click chuột). | Quan trọng nhất để phân tích hành vi người dùng chính xác. |
| **Ingestion Time** | Thời điểm dữ liệu được đưa vào hệ thống lưu trữ/Message Queue. | Để đo độ trễ của hệ thống ingestion. |
| **Process Time** | Thời điểm dữ liệu được xử lý/transform. | Để đo hiệu năng của Data Pipeline. |
| **Processing Time** | Thời gian hệ thống mất để xử lý một batch dữ liệu (tính bằng giây/phút). | Để tối ưu hóa performance. |

**Lời khuyên:** Luôn ghi lại các timestamp này (thường là tự động) để tracking dòng chảy dữ liệu và debug khi cần.

---

## 4. Phân tích Hệ thống Nguồn: Cơ sở dữ liệu (Databases)

Hiểu rõ Database là chìa khóa để thiết kế Data Pipeline hiệu quả.

### Các yếu tố cần cân nhắc chính
*   **Lookup & Index:** Database tìm kiếm dữ liệu như thế nào? (B-tree, LSM). Index giúp tăng tốc nhưng tốn bộ nhớ.
*   **Scaling:** Database có scale ngang (horizontal) hay dọc (vertical) không?
*   **Consistency:** Dữ liệu có đồng bộ mạnh (Strong Consistency) hay eventual consistency?
*   **CRUD Operations:** Cách thức tạo, đọc, cập nhật, xóa dữ liệu.

### Phân loại cơ sở dữ liệu

#### A. Relational Databases (RDBMS)
*   **Đặc điểm:** Dữ liệu dạng bảng (Table/Row), hỗ trợ ACID, Normalization (chuẩn hóa).
*   **Cấu trúc:** Dữ liệu được lưu theo hàng, truy xuất qua Primary Key và Foreign Key để Join.
*   **Use case:** Ideal cho các hệ thống giao dịch cần độ chính xác tuyệt đối và trạng thái thay đổi nhanh.
*   **Thách thức:** Làm sao capture được history (do bản chất là ghi đè dữ liệu)?

#### B. Non-Relational Databases (NoSQL)
Ra đời để giải quyết các bài toán quy mô lớn (Big Data) mà RDBMS không đáp ứng nổi.

**1. Key-Value Stores**
*   **Cơ chế:** Lấy dữ liệu qua Key (như Hash Map).
*   **Use case:** Caching (bộ nhớ đệm), session data. Tốc độ cực nhanh nhưng thường không bền vững (volatile).

**2. Document Stores (Ví dụ: MongoDB)**
*   **Cơ chế:** Lưu trữ đối tượng lồng nhau (JSON). Gọi là "Collection" thay vì Table.
*   **Ưu điểm:** Linh hoạt schema, không cần định nghĩa cứng.
*   **Nhược điểm:**
    *   Không hỗ trợ Join (phải xử lý ở application layer).
    *   Khó quản lý Schema Evolution (nếu không cẩn thận sẽ thành "Nightmare").
    *   Phải scan toàn bộ (Full scan) nếu không có Index để trích xuất dữ liệu phân tích, tốn kém chi phí Cloud.
*   **Lưu ý:** Hầu hết không hỗ trợ ACID mạnh (Eventual Consistency).

**3. Wide-Column Databases (Ví dụ: Cassandra, HBase)**
*   **Đặc điểm:** Tối ưu cho lượng dữ liệu khổng lồ (Petabytes), ghi (Write) cực nhanh, độ trễ cực thấp (<10ms).
*   **Cấu trúc:** Dữ liệu được nén theo cột.
*   **Use case:** IoT, Ad-tech, Real-time personalization.
*   **Hạn chế:** Chỉ hỗ trợ truy vấn qua Row Key (không có nhiều Index phức tạp). Không hỗ trợ truy vấn phức tạp như SQL.

**4. Graph Databases & Time Series**
*   **Graph:** Tối ưu cho dữ liệu quan hệ phức tạp (mạng lưới).
*   **Time Series:** Tối ưu cho dữ liệu chuỗi thời gian (dòng thời gian).

### Tóm lại cho Data Engineer
Khi làm việc với Source System, bạn cần xác định:
1.  Dữ liệu thuộc loại nào (Relational hay NoSQL)?
2.  Mô hình ghi dữ liệu là ghi đè (CRUD) hay chèn mới (Insert-only/CDC)?
3.  Yêu cầu về thời gian thực và độ trễ là bao nhiêu?
4.  Làm thế nào để trích xuất dữ liệu (Snapshot, CDC, hay Query Index) mà không làm sập hệ thống nguồn?

---

Dưới đây là bản t tổng hợp và dịch nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide** (Hướng dẫn ra quyết định) dành cho kỹ sư Data Engineering.

---

# Các Nguồn dữ liệu và Công cụ tích hợp (Phần II)

Tài liệu này tổng hợp các phương pháp và công cụ chính để trích xuất, tích hợp dữ liệu từ các hệ thống nguồn, tập trung vào việc **khi nào sử dụng**, **tại sao sử dụng**, và **ưu/nhược điểm** của từng giải pháp.

## 1. Cơ sở dữ liệu theo từng trường hợp đặc thù (Specialized Databases)

Khi dữ liệu có cấu trúc phức tạp hoặc yêu cầu hiệu năng đặc biệt, các cơ sở dữ liệu quan hệ truyền thống (RDBMS) có thể không tối ưu. Dưới đây là các lựa chọn thay thế phổ biến:

### Graph Databases (Cơ sở dữ liệu đồ thị)
**Tại sao dùng?**
Phù hợp để phân tích sự kết nối, mối quan hệ phức tạp giữa các thực thể (ví dụ: mạng xã hội, đồ thị gian lận,推荐系统).

**Khi nào dùng?**
*   Khi bạn cần thực hiện các truy vấn "traversal" (duyệt qua nhiều lớp kết nối), ví dụ: "Tìm bạn của bạn của bạn".
*   Phân tích cấu trúc đồ thị (nodes và edges).

**Ưu điểm:**
*   Tối ưu hóa cao cho các truy vấn dựa trên kết nối.
*   Mô hình dữ liệu linh hoạt cho cả nodes và edges.
*   Hỗ trợ các ngôn ngữ truy vấn chuyên biệt (Cypher, SPARQL, GQL).

**Nhược điểm:**
*   Khó khăn trong việc tích hợp nếu team quen với SQL hoặc dữ liệu phi cấu trúc.
*   Có thể gây quá tải hệ thống production nếu chạy các truy vấn lớn (nếu dùng cho transaction).

> **Lưu ý:** Có thể chuyển đổi dữ liệu đồ thị thành hàng trong RDBMS, nhưng sẽ mất đi hiệu năng tối ưu cho các truy vấn phức tạp.

### Search Databases (Cơ sở dữ liệu tìm kiếm)
**Tại sao dùng?**
Dành cho việc tìm kiếm văn bản (text search) và phân tích log.

**Khi nào dùng?**
*   **Text Search:** Tìm kiếm từ khóa, cụm từ chính xác hoặc tương tự (fuzzy matching) trong một khối lượng lớn văn bản.
*   **Log Analysis:** Phát hiện bất thường (anomaly detection), giám sát thời gian thực, phân tích bảo mật.

**Ưu điểm:**
*   Tốc độ tìm kiếm và truy xuất cực nhanh nhờ sử dụng chỉ mục (indexes).
*   Phổ biến trong các ứng dụng thương mại điện tử (tìm kiếm sản phẩm).

**Nhược điểm:**
*   Ít phổ biến hơn trong các pipeline dữ liệu truyền thống, nhưng thường xuất hiện trong các hệ thống hiện đại.

**Công cụ phổ biến:** Elasticsearch, Apache Solr, Lucene, Algolia.

### Time-Series Databases (Cơ sở dữ liệu chuỗi thời gian)
**Tại sao dùng?**
Tối ưu cho dữ liệu được ghi nhận theo thời gian (timestamp), thường là dữ liệu có tốc độ ghi (write) cao.

**Khi nào dùng?**
*   Dữ liệu IoT (nhiệt độ, cảm biến).
*   Logs ứng dụng, giao dịch tài chính (Fintech), quảng cáo (Ad tech).
*   Giám sát hệ thống (Operational analytics).

**Phân loại dữ liệu:**
*   **Measurement data:** Sinh ra đều đặn (ví dụ: cảm biến nhiệt độ).
*   **Event-based data:** Sinh ra khi có sự kiện (ví dụ: cảm biến chuyển động).

**Ưu điểm:**
*   Xử lý hiệu quả khối lượng dữ liệu lớn, tốc độ cao.
*   Thường dùng bộ nhớ đệm (memory buffering) để hỗ trợ ghi/đọc nhanh.

**Nhược điểm:**
*   Không tối ưu cho các tác vụ BI (Business Intelligence) phức tạp.
*   Ít thực hiện các phép nối (joins) dữ liệu.

---

## 2. Giao thức/API tích hợp

### REST API
**Tại sao dùng?**
Là tiêu chuẩn phổ biến nhất để trao đổi dữ liệu qua HTTP.

**Đặc điểm:**
*   **Stateless:** Mỗi lần gọi API là độc lập, không lưu trữ trạng thái phiên làm việc.
*   Chỉ sử dụng một số ít HTTP verbs (GET, POST, PUT, DELETE).

**Thách thức:**
*   Không phải là một đặc tả đầy đủ (chỉ là tập hợp các nguyên tắc).
*   Yêu cầu kỹ sư phải có nhiều kiến thức nghiệp vụ để sử dụng hiệu quả.

**Giải pháp:**
*   Sử dụng **Client Libraries** (thường là Python) để xử lý các boilerplate code (xác thực, ánh xạ phương thức).
*   Sử dụng các công cụ off-the-shelf để xây dựng pipeline ingestion từ REST.

### GraphQL
**Tại sao dùng?**
Là giải pháp thay thế linh hoạt hơn REST, cho phép lấy nhiều dữ liệu trong một lần запрос.

**Khi nào dùng?**
*   Khi bạn cần dữ liệu từ nhiều mô hình (models) khác nhau trong một request duy nhất.
*   Cần cấu trúc dữ liệu trả về linh hoạt (gần giống với JSON query).

**Ưu điểm:**
*   Giảm thiểu việc gọi API nhiều lần (over-fetching/under-fetching).

### Webhooks (Reverse API)
**Tại sao dùng?**
Mô hình truyền dữ liệu dựa trên sự kiện (event-based), nơi nguồn dữ liệu chủ động gửi dữ liệu về.

**Khi nào dùng?**
*   Khi cần nhận dữ liệu thời gian thực từ backend, web, hoặc mobile app khi có sự kiện xảy ra.
*   Dòng dữ liệu ngược chiều so với API thông thường (Source -> Sink).

**Xử lý:**
*   Thường kết hợp với **Message Queues** để xử lý lượng dữ liệu lớn, tốc độ cao.

### RPC (Remote Procedure Call) & gRPC
**Tại sao dùng?**
Cho phép gọi một hàm (procedure) trên hệ thống từ xa.

**Đặc điểm của gRPC:**
*   Developed by Google, sử dụng **Protocol Buffers** để serialization dữ liệu.
*   Tối ưu hiệu quả (CPU, băng thông) trên HTTP/2.
*   Có các tiêu chuẩn kỹ thuật nghiêm ngặt hơn REST, giúp dễ dàng tái sử dụng client libraries.

---

## 3. Chia sẻ dữ liệu (Data Sharing) & Nguồn dữ liệu bên thứ ba

### Data Sharing trong Cloud
**Tại sao dùng?**
Cho phép chia sẻ dữ liệu an toàn giữa các tenant (người dùng) trong hệ thống đa người dùng.

**Ưu điểm:**
*   **Data Marketplace:** Tạo ra chợ dữ liệu trung tâm, nơi nhà cung cấp có thể quảng bá và bán dữ liệu mà không lo quản lý quyền truy cập mạng phức tạp.
*   **Data Mesh:** Hỗ trợ mô hình quản lý dữ liệu phân tán, nơi các đơn vị tự quản lý dữ liệu và chia sẻ khi cần, giảm gánh nặng cho một trung tâm dữ liệu duy nhất.

### Third-Party Data Sources (Nguồn dữ liệu bên thứ 3)
**Tại sao dùng?**
Mọi công ty giờ đều là công ty công nghệ, họ muốn cung cấp dữ liệu cho khách hàng (API, Download, Cloud Sharing).

**Lợi ích:**
*   Tạo ra vòng lặp giá trị (Flywheel): Khách hàng tích hợp dữ liệu -> Tạo ra nhiều giá trị -> Dữ liệu ngày càng trở nên "dính" (sticky) với hệ thống của họ.

---

## 4. Message Queues & Event-Streaming Platforms

Đây là các hệ thống quan trọng trong kiến trúc hướng sự kiện (Event-driven), thường xuyên cắt ngang qua nhiều giai đoạn của vòng đời dữ liệu (từ nguồn đến ingestion).

### Message Queues (Hàng đợi thông điệp)
**Cơ chế:** Mô hình Publish-Subscribe. Dữ liệu được xuất bản (publish) và chuyển đến một hoặc nhiều người đăng ký (subscribers).

**Tại sao dùng?**
*   **Decoupling:** Tách rời các ứng dụng và hệ thống khỏi nhau (microservices).
*   **Buffering:** Xử lý các đợt tăng tải đột ngột (transient load spikes).
*   **Durability:** Lưu trữ tin nhắn bền vững thông qua kiến trúc phân tán (replication).

**Các yếu tố cần lưu ý:**
1.  **Message Ordering (Thứ tự):**
    *   **FIFO (First In, First Out):** Tin nhắn đến trước được xử lý trước.
    *   Hầu hết các hệ thống phân tán đều khó đảm bảo thứ tự tuyệt đối. Cần thiết kế hệ thống để xử lý trường hợp tin nhắn đến sai thứ tự.
2.  **Delivery Frequency (Tần suất giao):**
    *   **At least once:** Tin nhắn có thể bị gửi trùng lặp (phổ biến).
    *   **Exactly once:** Rất khó để đảm bảo tuyệt đối về mặt kỹ thuật.
    *   **Idempotent (Bất biến):** Hệ thống cần được thiết kế để xử lý tin nhắn trùng lặp mà không gây sai lệch kết quả (ví dụ: xử lý 1 lần hay 10 lần cũng cho kết quả giống nhau).
3.  **Scalability:** Có thể mở rộng ngang (horizontal scaling) để xử lý lượng lớn dữ liệu.

### Event-Streaming Platforms (Nền tảng truyền tải sự kiện)
**Khác biệt với Message Queue:**
*   Message Queue chủ yếu để **định tuyến** tin nhắn.
*   Event-Streaming Platform dùng để **ingest và xử lý** dữ liệu theo một nhật ký (log) được sắp xếp thứ tự.

**Đặc điểm chính:**
*   **Replayability:** Dữ liệu được lưu giữ một thời gian, cho phép tua lại (replay) tin nhắn từ quá khứ.
*   **Event Structure:** Bao gồm Key, Value, Timestamp.
*   **Topics:** Dòng sự kiện được chia thành các chủ đề (topics). Một topic có thể có nhiều producer và consumer (ví dụ: Topic "Đơn hàng" -> Consumer "Kho" và "Marketing").
*   **Stream Partitions (Phân vùng):** Chia một stream thành nhiều luồng con (như làn đường trên cao tốc) để tăng tốc độ xử lý song song (throughput). Tin nhắn cùng key sẽ vào cùng partition.

---

*Tài liệu tham khảo: Designing Data-Intensive Applications (Martin Kleppmann), các báo cáo thị trường về Graph Database.*

---

Chào bạn, tôi là chuyên gia Data Engineering. Dưới đây là bản dịch và tổng hợp nội dung bạn yêu cầu, được trình bày theo phong cách Decision Guide với cấu trúc Markdown rõ ràng.

***

# PART II: Tổng quan và Ra quyết định về Hệ thống Nguồn (Source Systems)

Phần này tập trung vào các yếu tố quyết định khi làm việc với hệ thống nguồn, bao gồm cách xử lý luồng dữ liệu, các bên liên quan và các yếu tố "ngầm" (Undercurrents) ảnh hưởng đến kiến trúc dữ liệu.

## 1. Phân vùng trong Luồng Dữ liệu (Stream Partitioning)

### Tại sao cần phân vùng?
Phân vùng (Partitioning) cho phép chia nhỏ luồng dữ liệu thành các phần độc lập để xử lý song song. Điều này giúp tăng throughput và đảm bảo các dữ liệu liên quan được xử lý cùng nhau.

### Khi nào nên dùng?
*   Khi bạn cần xử lý lượng lớn dữ liệu stream theo thời gian thực.
*   Khi các message trong cùng một phiên/giao dịch cần được xử lý bởi cùng một server (ví dụ: tin nhắn IoT từ cùng một thiết bị).

### Ưu nhược điểm & Ra quyết định

| Tiêu chí | Phân tích | Quyết định |
| :--- | :--- | :--- |
| **Cách hoạt động** | Sử dụng **Partition Key** (khóa phân vùng). Ví dụ: `ID % 3` để chia thành 3 partition (0, 1, 2). | Chọn key dựa trên logic chia đều dữ liệu. |
| **Hotspotting (Điểm nóng)** | Nếu key phân vùng không đều (ví dụ: dùng tiểu bang làm key, dữ liệu từ California sẽ quá tải partition đó). | **CẢNH BÁO:** Đảm bảo Partition Key phân phối dữ liệu đều khắp các partition để tránh mất cân bằng tải. |
| **Lợi ích** | Đảm bảo tính **Fault Tolerance** (chịu lỗi) và **Resilience** (phục hồi). Nếu một node chết, node khác thay thế mà không mất dữ liệu. | Nên dùng khi cần hệ thống ổn định, liên tục. |

---

## 2. Các bên liên quan (Whom You’ll Work With)

### Tại sao cần quan tâm?
Dữ liệu đến từ hệ thống của người khác. Bạn không thể kiểm soát hoàn toàn nguồn dữ liệu, nên mối quan hệ và sự hợp tác là chìa khóa thành công.

### Khi nào cần tương tác?
Luôn luôn. Đặc biệt khi:
*   Truy cập nguồn dữ liệu.
*   Có thay đổi về schema hoặc dữ liệu.
*   Hệ thống nguồn gặp sự cố.

### Các loại Stakeholder

| Nhóm | Vai trò | Ví dụ |
| :--- | :--- | :--- |
| **Systems Stakeholder** | Xây dựng & duy trì hệ thống nguồn. | Software Engineers, DevOps, Third-party vendors. |
| **Data Stakeholder** | Sở hữu & kiểm soát quyền truy cập dữ liệu. | IT, Data Governance team, Third-party data providers. |

### Ra quyết định: Thiết lập quy trình làm việc
1.  **Data Contract (Hợp đồng dữ liệu):** Một thỏa thuận bằng văn bản giữa bạn và chủ hệ thống nguồn. Nó định nghĩa:
    *   Dữ liệu nào được trích xuất (Full hay Incremental).
    *   Tần suất lấy dữ liệu.
    *   Cách thức liên hệ khi có vấn đề.
    *   *Lưu trữ:* GitHub repo hoặc tài liệu nội bộ.
2.  **SLA (Service Level Agreement):** Cam kết về chất lượng và uptime của dữ liệu (ví dụ: "Dữ liệu có sẵn 99% thời gian").
3.  **Phản hồi (Feedback Loop):** Tạo kênh thông báo để hệ thống nguồn cảnh báo bạn về các thay đổi schema hoặc sự cố trước khi nó gây hại cho pipeline của bạn.

---

## 3. Các yếu tố "Ngầm" (Undercurrents) ảnh hưởng đến Hệ thống Nguồn

Đây là các khía cạnh bảo mật, quản lý và kiến trúc bạn phải xem xét khi kết nối với hệ thống nguồn.

### A. Bảo mật (Security)
*   **Tại sao:** Để tránh tạo lỗ hổng cho hệ thống nguồn và dữ liệu của bạn.
*   **Quyết định:**
    *   Kiểm tra xem dữ liệu được mã hóa khi lưu trữ (**Encryption at rest**) và khi truyền tải (**Encryption in transit**) hay không.
    *   Sử dụng **VPN** thay vì truy cập qua internet công cộng.
    *   Quản lý bí mật (Secrets) an toàn: Sử dụng Key Manager cho SSH keys, Password Manager/SSO cho mật khẩu.
    *   Xác minh tính hợp lệ của nguồn dữ liệu (Trust but verify).

### B. Quản lý dữ liệu (Data Management)
*   **Tại sao:** Bạn cần hiểu cách dữ liệu được quản lý bởi hệ thống nguồn để biết cách Ingest và Transform phù hợp.
*   **Quyết định:**
    *   **Data Governance:** Ai quản lý dữ liệu?
    *   **Data Quality:** Làm thế nào đảm bảo dữ liệu sạch? (Thiết lập kỳ vọng với đội nguồn).
    *   **Schema:** Luôn chờ đợi Schema thay đổi. Cần cơ chế thông báo trước.
    *   **Privacy & Ethics:** Dữ liệu có bị che mờ (obfuscated)? Tính hợp pháp?

### C. DataOps & Operational Excellence
*   **Tại sao:** Để đảm bảo tính ổn định và khả năng quan sát (Observability) hệ thống nguồn.
*   **Quyết định:**
    *   **Observability:** Bạn cần monitor uptime của hệ thống nguồn. Nếu nguồn chết, pipeline của bạn cũng chết.
    *   **Incident Response:** Kế hoạch dự phòng khi nguồn mất dữ liệu? (Backfill như thế nào?).
    *   **Automation:** Tự động hóa nhưng cần tách bạch (Decouple) để lỗi ở hệ thống nguồn không làm tê liệt hoàn toàn pipeline của bạn.

### D. Kiến trúc dữ liệu (Data Architecture)
*   **Tại sao:** Hiểu điểm mạnh/yếu của kiến trúc nguồn giúp bạn thiết kế pipeline tốt hơn.
*   **Quyết định:**
    *   **Reliability:** Hệ thống có ổn định không? Tần suất lỗi?
    *   **Durability:** Xử lý như thế nào khi mất hardware hoặc network?
    *   **Availability:** Đảm bảo hệ thống sẵn sàng khi cần.

### E. Orchestration (Phối hợp công việc)
*   **Tại sao:** Để pipeline của bạn có thể gọi/truy cập hệ thống nguồn đúng cách.
*   **Quyết định:**
    *   **Network Access:** Đảm bảo Authentification & Authorization đúng.
    *   **Cadence:** Dữ liệu có sẵn theo lịch cố định hay không?
    *   **Container:** Có dùng chung Kubernetes cluster không? (Cân giữa lợi ích integration và rủi ro tight coupling).

### F. Kỹ thuật phần mềm (Software Engineering)
*   **Tại sao:** Bạn thường phải viết code để truy cập nguồn.
*   **Quyết định:**
    *   **Access Patterns:** Dùng API (REST/GraphQL) hay Database Driver?
    *   **Handling:** Xử lý Retries, Timeouts, Pagination như thế nào?
    *   **Deployment:** Code của bạn có tích hợp được với Orchestration framework (như Airflow) không?

---

## 4. Kết luận & Lời khuyên

### Tổng kết
Làm Data Engineering không chỉ là xử lý dữ liệu sau khi đã có sẵn, mà còn phải quản lý mối quan hệ và sự ổn định của **Hệ thống Nguồn (Source Systems)**.

### Lời khuyên chiến lược
1.  **Đừng coi nguồn là "vấn đề của người khác":** Nếu hệ thống nguồn sập, bạn sẽ là người chịu trách nhiệm đầu tiên.
2.  **Hợp tác hai chiều:** Thiết lập Data Contract và SLA. Chủ động thông báo cho đội nguồn về nhu cầu dữ liệu của bạn.
3.  **Tận dụng xu hướng mới:**
    *   **Reverse ETL:** Đưa dữ liệu trở lại hệ thống nguồn.
    *   **Event-Streaming:** Hệ thống nguồn có thể vừa là nguồn vừa là người tiêu dùng dữ liệu (Data Engineering System).
4.  **Tạo Data Product:** Hợp tác với đội ứng dụng để tạo ra giá trị cho người dùng cuối (User-facing data products).

### Tài nguyên bổ sung (Tham khảo)
*   Confluent’s “Schema Evolution and Compatibility”
*   Database Internals (Alex Petrov)
*   “The Log” by Jay Kreps (Về Real-time data abstraction)
*   ... và các tài liệu về NoSQL, DynamoDB, Deequ (Data Quality testing).

---

Dưới đây là bản dịch và tổng hợp nội dung từ chương "Storage" (Chương 6) của sách, được chuyển đổi theo phong cách **Decision Guide** dành cho Data Engineer.

---

# Storage (Lưu trữ) - Quyết định Kiến trúc & Công nghệ

## 1. Tổng quan: Vai trò của Storage trong Data Engineering Lifecycle

Storage không chỉ là nơi dữ liệu "nằm yên", mà là trung tâm của vòng đời dữ liệu (Data Pipeline). Trong khi Source Systems (hệ thống nguồn) thường thuộc sự kiểm soát của các bộ phận khác, Data Engineer chịu trách nhiệm trực tiếp đối với Storage trong suốt quá trình từ **Ingestion** (tiếp nhận) đến **Serving** (phục vụ phân tích).

### Phân cấp Storage (Theo chiều dọc chi phí & hiệu năng)
Hiểu rõ các thành phần thô (Raw Ingredients) là chìa khóa để đánh đổi giữa chi phí và hiệu năng:

| Cấp độ | Loại Storage | Đặc điểm | Chi phí (Approx) | Quyết định khi dùng |
| :--- | :--- | :--- | :--- | :--- |
| **Cao nhất** | **CPU Cache** | Tích hợp trên chip, truy cập tức thời (ns) | N/A | Tối ưu hóa code, không can thiệp trực tiếp. |
| **Cao** | **RAM (Memory)** | Volatile (bay hơi khi mất điện), cực nhanh | ~$10/GB | Dùng cho **Caching**, xử lý thời gian thực, index database. |
| **Trung bình** | **SSD** | Không cơ khí, truy cập ngẫu nhiên nhanh | ~$0.20/GB | Dùng cho **OLTP**, Database cần IOPS cao, Cache layer cho Data Lake. |
| **Thấp** | **HDD (Magnetic)** | Cơ khí (đĩa quay), chậm hơn nhưng dung lượng lớn | ~$0.03/GB | Dùng cho **Data Lake (Object Storage)**, lưu trữ khối lượng lớn (Bulk). |
| **Rất thấp** | **Archival** | Truy cập rất chậm (giờ/ngày) | ~$0.004/GB | Dùng cho **Backup**, tuân thủ pháp lý (Cold Data). |

---

## 2. Raw Ingredients: Thành phần cơ bản của Storage

Trước khi quyết định hệ thống lưu trữ nào, Data Engineer cần hiểu các thành phần vật lý và kỹ thuật cơ bản.

### A. Magnetic Disk Drive (HDD)
*   **Cơ chế:** Đĩa từ quay, đầu đọc/ghi cơ khí.
*   **Tại sao dùng?**
    *   **Chi phí/Gigabyte:** Rẻ nhất (khoảng 3 cent/GB).
    *   **Throughput:** Rất cao khi đọc tuần tự (do tính chất vật lý).
*   **Khi nào không dùng?**
    *   Khi cần **Random Access** (truy cập ngẫu nhiên) nhanh.
    *   Khi cần **IOPS** (Số lượng thao tác I/O mỗi giây) cao.
*   **Hạn chế:**
    *   **Latency:** Do cơ chế cơ khí (Seek time + Rotational latency ~ 4ms+).
    *   **Tốc độ không tỷ lệ thuận dung lượng:** Dung lượng tăng 4x thì tốc độ chỉ tăng 2x.

### B. Solid-State Drive (SSD)
*   **Cơ chế:** Lưu trữ điện tử (Flash memory), không có bộ phận chuyển động.
*   **Tại sao dùng?**
    *   **Random Access:** Cực nhanh (< 0.1ms).
    *   **IOPS:** Cao gấp hàng chục, hàng trăm lần HDD.
    *   **OLTP:** Tiêu chuẩn cho các hệ thống giao dịch (PostgreSQL, MySQL).
*   **Khi nào cân nhắc chi phí?**
    *   Chi phí đắt gấp ~10 lần HDD. Do đó, thường không phải là lựa chọn mặc định cho **Data Lake** quy mô lớn (nơi lưu trữ hàng Petabyte).

### C. Random Access Memory (RAM)
*   **Đặc tính:** Volatile (mất điện là mất dữ liệu), cực nhanh (100ns).
*   **Quyết định:**
    *   Dùng cho **Caching**: Lưu dữ liệu truy cập thường xuyên.
    *   Dùng cho **In-memory Database**: Tốc độ tối ưu nhưng rủi ro mất dữ liệu nếu không có cơ chế backup ra đĩa (Persistence).
    *   **Cost:** Cực kỳ đắt ($10/GB).

### D. Networking & CPU (Yếu tố phân phối)
*   **Vai trò:** Storage hiện đại là **Distributed System**.
*   **Quyết định:**
    *   Đừng chỉ nhìn vào đĩa cứng, hãy nhìn vào **Network Bandwidth**.
    *   **Parallelism:** Đọc từ 1000 đĩa cùng lúc qua mạng nhanh hơn nhiều so với 1 đĩa đơn lẻ.
    *   **Availability Zones:** Phân phối dữ liệu qua các Zone để tăng độ bền (Durability) và sẵn sàng (Availability).

---

## 3. Kỹ thuật phần mềm: Serialization & Compression

### A. Serialization (Nén cấu trúc dữ liệu)
*   **Là gì?** Quá trình chuyển đổi cấu trúc dữ liệu từ RAM sang định dạng lưu trữ/để truyền đi.
*   **Tại sao quan trọng?** Ảnh hưởng trực tiếp đến hiệu năng truy vấn và dung lượng lưu trữ.
*   **Quyết định lựa chọn định dạng:**
    *   **Row-based (CSV, JSON):** Tốt cho ghi (Write), đọc theo dòng (OLTP).
    *   **Columnar (Apache Parquet, ORC):** Tốt cho đọc (Read), nén dữ liệu tốt, tối ưu cho **OLAP/Analytics**.
    *   **Hybrid/In-memory (Apache Arrow, Avro):** Tối ưu cho trao đổi giữa các tiến trình (IPC) và xử lý song song.

### B. Compression (Nén dữ liệu)
*   **Tại sao dùng?**
    1.  **Giảm dung lượng:** Tiết kiệm chi phí lưu trữ (đặc biệt trên Cloud).
    2.  **Tăng tốc độ Scan:** Đọc ít byte hơn từ đĩa/network.
    3.  **Tăng hiệu quả Network:** Giảm băng thông cần thiết (ví dụ: nén 10:1 giúp tăng hiệu quả băng thông gấp 10 lần).
*   **Nhược điểm:** Tiêu tốn CPU để nén/giải nén.
*   **Quyết định:** Chọn thuật toán nén (Snappy, Gzip, Zstd...) cân bằng giữa tỷ lệ nén và tốc độ CPU.

### C. Caching (Bộ nhớ đệm)
*   **Là gì?** Lưu dữ liệu truy cập thường xuyên vào tầng lưu trữ nhanh hơn.
*   **Chiến lược:**
    *   **Cache Hierarchy:** Xây dựng các tầng (Layer) từ CPU Cache -> RAM -> SSD -> HDD.
    *   **Reverse Cache (Archival):** Lưu trữ giá rẻ (Glacier/S3 Deep Archive) nhưng truy cập rất chậm, dùng cho dữ liệu chết (Cold Data).

---

## 4. Data Storage Systems & Architectures

### A. Single Machine vs. Distributed Storage
*   **Single:** Đơn giản, dễ quản lý, nhưng giới hạn bởi dung lượng và hiệu năng của 1 máy.
*   **Distributed:** Phân tán dữ liệu lên nhiều server.
    *   **Lợi ích:** Khả năng mở rộng (Scalability), Tolerant (chịu lỗi khi 1 node chết).
    *   **Công nghệ:** HDFS, Cloud Object Storage (S3), Cloud Data Warehouse (Snowflake, BigQuery).

### B. Consistency Models (Mô hình nhất quán)
Khi dữ liệu phân tán, làm sao đảm bảo dữ liệu đúng?

| Mô hình | Đặc điểm | Ưu điểm | Nhược điểm | Phù hợp |
| :--- | :--- | :--- | :--- | :--- |
| **Strong Consistency** | Đọc luôn ra dữ liệu mới nhất ngay sau khi ghi. | An toàn, dễ hiểu. | chậm hơn, độ trễ cao (Latency). | Hệ thống tài chính, giao dịch tiền (Banking). |
| **Eventual Consistency** | Hệ thống "hứa" sẽ đồng bộ sau, dữ liệu có thể cũ trong thời gian ngắn. | Tốc độ cao, sẵng sàng phục vụ (High Availability). | Có thể đọc sai dữ liệu cũ (Stale data). | Social Media, Analytics, Data Lake (không cần realtime 100%). |

*   **ACID:** (Atomicity, Consistency, Isolation, Durability) - Dùng cho Transactional DB.
*   **BASE:** (Basically Available, Soft state, Eventual consistency) - Dùng cho Big Data, NoSQL.

---

## Kết luận: Decision Guide tóm tắt

1.  **Nếu bạn cần Speed (Tốc độ):** Chọn **SSD** hoặc **RAM**. Sử dụng **Columnar Format (Parquet)** và **Compression** để tối ưu I/O.
2.  **Nếu bạn cần Scale & Cost (Quy mô & Chi phí):** Chọn **HDD (Object Storage)**. Chấp nhận **Eventual Consistency** nếu có thể.
3.  **Nếu bạn cần Durability (Độ bền):** Phân phối dữ liệu qua **Nhiều Availability Zone**.
4.  **Luôn nhớ:** Storage là một **Web Application** với API (HTTP/REST), không chỉ là cái ổ cứng vật lý.

---

Chào bạn, tôi là chuyên gia Data Engineering. Dưới đây là bản dịch và tổng hợp nội dung bạn yêu cầu, được trình bày theo định dạng Markdown và phong cách "Decision Guide".

***

# PART II: HƯỚNG DẪN RA QUYẾT ĐỊNH VỀ KIẾN TRÚC LƯU TRỮ DỮ LIỆU

Phần này tập trung vào các quyết định liên quan đến lưu trữ dữ liệu (Data Storage), từ các hệ thống file cơ bản đến các giải pháp lưu trữ đám mây hiện đại. Chúng ta sẽ xem xét các lựa chọn về **Storage** (lưu trữ) và cách chúng ảnh hưởng đến các **Data Pipeline** (luồng dữ liệu).

## 1. Consistency (Tính nhất quán)

### Tại sao dùng?
Tính nhất quán là một trong những khía cạnh quan trọng nhất cần cân nhắc khi thiết kế hệ thống dữ liệu, đặc biệt là các hệ thống phân tán. Nó xác định dữ liệu có chính xác và cập nhật ở mọi thời điểm hay không.

### Khi nào dùng?
Quyết định về mức độ nhất quán thường được đưa ra ở ba cấp độ:
1.  **Công nghệ Database:** Chọn loại database (SQL vs NoSQL) sẽ định nghĩa mức độ nhất quán mặc định.
2.  **Cấu hình Database:** Các tham số cấu hình có thể điều chỉnh mức độ này.
3.  **Cấp độ Query:** Một số database cho phép xác định mức độ nhất quán cho từng câu lệnh truy vấn riêng lẻ.

### Ưu nhược điểm (So sánh BASE vs Strong Consistency)

| Đặc điểm | **BASE (Eventual Consistency)** | **Strong Consistency** |
| :--- | :--- | :--- |
| **Mô tả** | Là mô hình đối lập với ACID. Gồm các thành phần: <br> - **Basically Available:** Dữ liệu có sẵn hầu hết thời gian. <br> - **Soft-state:** Trạng thái giao dịch không chắc chắn. <br> - **Eventual consistency:** Đọc dữ liệu cuối cùng sẽ trả về giá trị nhất quán. | Hệ thống đảm bảo rằng mọi ghi vào bất kỳ node nào đều được phân phối đồng thuận trước, và mọi đọc từ database đều trả về giá trị nhất quán. |
| **Tại sao dùng?** | Để **scale ngang (horizontal scaling)** xử lý lượng dữ liệu lớn với tốc độ cao. | Khi cần **độ chính xác tuyệt đối** của dữ liệu ở mọi thời điểm. |
| **Khi nào dùng?** | Phù hợp cho các hệ thống phân tán quy mô lớn, nơi tốc độ và khả năng mở rộng là ưu tiên hàng đầu. | Phù hợp cho các ứng dụng tài chính, giao dịch quan trọng, nơi dữ liệu sai lệch là không thể chấp nhận được. |
| **Nhược điểm** | Không đảm bảo dữ liệu luôn mới nhất; có thể trả về dữ liệu cũ. | **Độ trễ truy vấn (latency) cao hơn** và tiêu tốn nhiều tài nguyên hơn. |

> **Lời khuyên cho Data Engineer:** Bạn cần thương lượng các yêu cầu về tính nhất quán với các bên liên quan (kỹ thuật và kinh doanh). Đây là vấn đề công nghệ lẫn tổ chức. Hãy đảm bảo bạn hiểu rõ database của mình xử lý consistency như thế nào.

---

## 2. File Storage (Lưu trữ theo File)

### Tại sao dùng?
File storage là mô hình lưu trữ quen thuộc, mô phỏng theo hệ thống file trên máy tính cá nhân. Nó tổ chức dữ liệu thành các file và thư mục (directory tree).

### Khi nào dùng?
- Khi pipeline của bạn cần các cấu trúc file truyền thống.
- **Cần cẩn trọng:** Chỉ sử dụng cho các bước **nhập liệu một lần (one-time ingestion)** hoặc giai đoạn **thám hiểm (exploratory)** của pipeline development.
- **Hạn chế:** Tránh sử dụng cho các môi trường có trạng thái (stateful) lâu dài. Thay vào đó, hãy dùng **ephemeral environments** (môi trường tạm thời) và **Object Storage** cho lưu trữ trung gian.

### Các loại File Storage phổ biến

#### a. Local Disk Storage (Lưu trữ đĩa cục bộ)
- **Mô tả:** Hệ thống file quản lý bởi OS trên phân vùng SSD hoặc đĩa từ (NTFS, ext4).
- **Ưu điểm:** Hỗ trợ **full read-after-write consistency**; có các tính năng nâng cao như journaling, snapshots, RAID.
- **Nhược điểm:** Giới hạn về quy mô và độ sẵn sàng.

#### b. Network-Attached Storage (NAS)
- **Mô tả:** Cung cấp hệ thống file qua mạng lưới.
- **Ưu điểm:** ảo hóa lưu trữ, dự phòng, chia sẻ file giữa nhiều máy.
- **Lưu ý:** Hiệu suất có thể thấp hơn do truy cập qua mạng. Cần kiểm tra mô hình consistency nếu nhiều client truy cập cùng lúc.

#### c. Cloud Filesystem Services (Dịch vụ hệ thống file đám mây)
- **Ví dụ:** Amazon EFS.
- **Mô tả:** Hệ thống file được quản lý hoàn toàn, hoạt động như NAS nhưng do nhà cung cấp đám mây xử lý chi tiết mạng và cấu hình.
- **Ưu điểm:** Tự động mở rộng, thanh toán theo dung lượng sử dụng, h hỗ trợ read-after-write consistency và open-after-close consistency.

---

## 3. Block Storage (Lưu trữ theo Khối)

### Tại sao dùng?
Đây là dạng lưu trữ thô (raw storage) cơ bản nhất (SSD/đĩa từ). Nó cho phép kiểm soát chi tiết dung lượng, khả năng mở rộng và độ bền dữ liệu.

### Khi nào dùng?
- **Hệ thống Database giao dịch (Transactional database):** Để tối ưu hóa hiệu suất bố trí dữ liệu.
- **Boot disk trên Cloud VM:** Là lựa chọn mặc định để khởi động hệ điều hành.
- **Cần hiệu suất cao và độ trễ thấp:** Khi dữ liệu cần được truy cập ngẫu nhiên với tốc độ nhanh nhất.

### Các loại Block Storage và Kiến trúc

#### a. RAID (Redundant Array of Independent Disks)
- **Mục đích:** Kiểm soát nhiều đĩa đồng thời để cải thiện độ bền dữ liệu (durability), hiệu suất và dung lượng.
- **Cơ chế:** Nhiều sơ đồ mã hóa và sẵng sàng (parity) để cân bằng giữa băng thông và khả năng chịu lỗi.

#### b. Storage Area Network (SAN)
- **Mô tả:** Cung cấp thiết bị block storage ảo hóa qua mạng lưới, thường từ một pool lưu trữ.
- **Ưu điểm:** Tinh chỉnh khả năng mở rộng, hiệu suất và độ sẵn sàng.

#### c. Cloud Virtualized Block Storage (Block storage ảo hóa đám mây)
- **Ví dụ:** Amazon EBS.
- **Mô tả:** Lưu trữ tách biệt với instance host nhưng cùng zone để đảm bảo hiệu suất cao và độ trễ thấp.
- **Ưu điểm:**
    - **Persistence (Lưu trữ bền vững):** Dữ liệu tồn tại ngay cả khi instance bị xóa hoặc tắt.
    - **Replication (Nhân bản):** Dữ liệu được sao chép sang ít nhất 2 máy chủ riêng biệt.
    - **Snapshot:** Chụp nhanh trạng thái dữ liệu tại một thời điểm (point-in-time).
    - **Mở rộng:** Có thể mở rộng dung lượng và IOPS lên rất lớn.

#### d. Local Instance Volumes (Volume thực thể cục bộ)
- **Mô tả:** Lưu trữ được gắn vật lý vào máy chủ host (ví dụ: Instance Store trên AWS EC2).
- **Ưu điểm:** Chi phí thấp (hoặc miễn phí), độ trễ thấp, IOPS cao.
- **Nhược điểm (Rủi ro lớn):**
    - **Mất dữ liệu khi tắt máy:** Dữ liệu biến mất vĩnh viễn nếu instance bị shutdown hoặc delete.
    - **Không có replication:** Nếu đĩa vật lý hỏng, dữ liệu mất.
    - **Không hỗ trợ snapshot hoặc backup.**
- **Khi nào dùng?** Dùng làm **local cache** cho các job tạm thời (ephemeral job), ví dụ xử lý dữ liệu trên EMR cluster. Chỉ dùng khi rủi ro mất dữ liệu không gây hậu quả nghiêm trọng.

---

## 4. Object Storage (Lưu trữ theo Đối tượng)

### Tại sao dùng?
Object storage là tiêu chuẩn vàng cho **Data Lake** và các ứng dụng dữ liệu lớn hiện đại (Big Data). Nó lưu trữ các đối tượng (file) bất biến (immutable) trong các container logic (bucket).

### Khi nào dùng?
- **Dữ liệu lớn (Big Data):** Đọc và ghi hàng loạt (batch read/write) với tốc độ cao.
- **Data Lake & Data Warehouse:** Lưu trữ lớp dữ liệu thô và đã qua xử lý.
- **Dữ liệu không cấu trúc:** Lưu trữ bất kỳ loại dữ liệu nhị phân nào (hình ảnh, video, âm thanh, log).
- **Phân tách tính toán và lưu trữ (Compute/Storage Separation):** Cho phép xử lý dữ liệu bằng các cụm (cluster) tạm thời.

### Ưu nhược điểm và Đặc điểm kỹ thuật

| Đặc điểm | Mô tả | Decision Guide |
| :--- | :--- | :--- |
| **Độ bền (Durability)** | Lưu trữ ở nhiều Availability Zone (AZ). | **Cao hơn nhiều** so với Block storage cục bộ. Phù hợp lưu trữ vĩnh viễn. |
| **Kiến trúc** | **Key-Value Store** (Khóa - Giá trị). Không có cấu trúc thư mục thực sự (Directory Tree). | Cần hiểu rõ: "Thư mục" thực chất là một phần của tên file (Key). Truy vấn theo tiền tố (prefix) có thể chậm nếu bucket chứa hàng triệu đối tượng. |
| **Tính bất biến (Immutability)** | Ghi một lần (Write Once). Không thể sửa đổi tại chỗ (no in-place updates). | Để sửa đổi, phải ghi đè toàn bộ đối tượng. Phù hợp cho dữ liệu lịch sử, không phù hợp cho giao dịch realtime nhiều update nhỏ. |
| **Consistency** | Tùy thuộc nhà cung cấp (ví dụ: S3 trước đây là Eventual, hiện tại là Strongly Consistent cho cả read/write sau khi tạo). | Cần kiểm tra kỹ tài liệu để đảm bảo dữ liệu nhất quán cho ứng dụng của bạn. |
| **Versioning** | Hỗ trợ quản lý phiên bản (versioning) để khôi phục dữ liệu. | Rất hữu ích cho việc quản lý dữ liệu trong Data Lake. |

### So sánh với File/Block Storage
- **Object Storage:** Lý tưởng cho lưu trữ vĩnh viễn, dữ liệu lớn, phân tích (OLAP), và ML pipelines.
- **Block Storage:** Lý tưởng cho database giao dịch, boot disk, và các workload cần IOPS cao.
- **File Storage:** Lý tưởng cho các ứng dụng legacy hoặc cần cấu trúc thư mục phức tạp.

> **Tóm tắt cho Data Engineer:** Object Storage là nền tảng của Data Lakehouse hiện đại (với các công cụ như Apache Hudi, Delta Lake để xử lý update/delete). Nó cho phép lưu trữ lượng dữ liệu khổng lồ (Exabytes) với chi phí hợp lý và khả năng mở rộng gần như vô hạn (giới hạn bởi ngân sách).

---

Dưới đây là bản dịch và tổng hợp nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide (Hướng dẫn ra quyết định)** tập trung vào bối cảnh lưu trữ dữ liệu trong hệ thống Data Engineering.

***

# Quyết định Lưu trữ Dữ liệu: Kiến trúc và Chiến lược

Phần này t tổng hợp các quyết định quan trọng liên quan đến việc lựa chọn và tối ưu hóa hệ thống lưu trữ dữ liệu (Data Storage), từ lưu trữ đối tượng (Object Store) đến cơ sở dữ liệu phân tích (Analytical Databases).

## 1. Kiểm soát Tính nhất quán (Consistency) trong Object Store

Hầu hết các hệ thống Object Store (như S3, GCS) tuân theo mô hình **Eventual Consistency** (Tính nhất quán cuối cùng). Điều này khác biệt với mô hình **Strong Consistency** (Tính nhất quán mạnh) mà chúng ta thường thấy ở ổ cứng cục bộ.

### Tại sao cần Strong Consistency?
Bạn cần đảm bảo rằng sau khi ghi dữ liệu, việc đọc ngay lập tức sẽ trả về dữ liệu mới nhất (không bị lỗi đọc cũ - stale read).

### Cách triển khai (Implementation)
Để đạt được Strong Consistency trên Object Store, kiến trúc sư dữ liệu thường áp dụng phương pháp sau:
1.  **Ghi đối tượng:** Lưu dữ liệu vào Object Store.
2.  **Ghi metadata:** Lưu thông tin phiên bản (hash hoặc timestamp) vào một database có Strong Consistency (ví dụ: PostgreSQL).

**Quy trình đọc (Read Path):**
1.  Truy vấn database để lấy metadata mới nhất.
2.  So sánh metadata này với Object Store.
3.  Nếu khớp -> Trả về dữ liệu. Nếu không -> Lặp lại cho đến khi tìm thấy phiên bản mới nhất.

### Nhược điểm
*   **Latency cao:** Quá trình kiểm tra kép làm tăng thời gian truy cập dữ liệu.

---

## 2. Object Versioning (Phiên bản đối tượng)

Khi bạn ghi đè lên một đối tượng tồn tại, hệ thống thực chất đang tạo một đối tượng mới và cập nhật các tham chiếu.

### Tại sao dùng Versioning?
*   **Giải quyết vấn đề Stale Read:** Giúp tránh nhầm lẫn khi dữ liệu đang được cập nhật liên tục.
*   **Khôi phục dữ liệu:** Cho phép truy xuất các phiên bản cũ của dữ liệu.

### Cơ chế hoạt động
*   Hệ thống giữ lại các pointer (con trỏ) đến các phiên bản cũ.
*   **Lưu ý quan trọng:** Object Store thường lưu trữ **toàn bộ** dữ liệu của mỗi phiên bản (full object), không phải chỉ các thay đổi (differential snapshots).

### Quyết định Cost (Chi phí)
*   **Rủi ro:** Lưu trữ nhiều phiên bản làm tăng chi phí lưu trữ đáng kể.
*   **Giải pháp:** Sử dụng **Lifecycle Policies** (Chính sách vòng đời) để tự động xóa các phiên bản cũ hoặc chuyển chúng sang các tier lưu trữ rẻ hơn (Archival) sau một độ tuổi nhất định.

---

## 3. Storage Classes and Tiers (Phân loại lưu trữ)

Các nhà cung cấp đám mây (Cloud Vendors) cung cấp các lớp lưu trữ khác nhau dựa trên tần suất truy cập và độ sẵn sàng.

### Khi nào nên dùng các Tier thấp hơn?
Khi dữ liệu cần lưu trữ lâu dài nhưng không cần truy cập thường xuyên (Cold Data).

### So sánh các Tier (Ví dụ dựa trên AWS S3)

| Tính năng | **Standard / Hot Storage** | **Infrequent Access (IA)** | **Archival (Glacier)** |
| :--- | :--- | :--- | :--- |
| **Mục đích** | Dữ liệu truy cập thường xuyên | Dữ liệu truy cập ít (vài lần/tháng) | Dữ liệu lưu trữ dài hạn (năm) |
| **Chi phí Lưu trữ** | Cao | Thấp hơn | Rất thấp ($1/TB/tháng) |
| **Chi phí Truy xuất (Retrieval)** | Thấp | Cao hơn (phạt nếu truy xuất sớm) | Rất cao (tốn kém nếu cần lấy gấp) |
| **Thời gian truy xuất** | Tức thì | Tức thì hoặc vài giờ | Từ phút đến **12 giờ** |
| **Độ sẵn sàng (Availability)** | 99.99% | 99.9% - 99.5% | Thấp hơn (tùy tier) |

### Cảnh báo (Warning)
Đừng để bị lừa bởi chi phí lưu trữ rẻ của **Archival**. Nếu bạn cần truy xuất dữ liệu thường hơn dự kiến, chi phí lấy dữ liệu (Data Retrieval Cost) có thể "phá sản" ngân sách của bạn.

---

## 4. Filesystems dựa trên Object Store (S3FS, File Gateway)

Các công cụ như `s3fs` hoặc Amazon S3 File Gateway cho phép mount một bucket Object Store thành một ổ đĩa hệ thống tệp (Filesystem) cục bộ.

### Khi nào nên dùng?
*   Khi cần truy cập dữ liệu Object Store thông qua các công cụ file system truyền thống.
*   Dữ liệu cập nhật không thường xuyên.

### Hạn chế (Limitation)
*   **Write Performance:** Object Store không được tối ưu hóa cho các giao dịch ghi tốc độ cao (high-speed transactional writing). Việc ghi quá nhiều nhỏ lẻ (small writes) sẽ làm hệ thống quá tải.
*   **Phù hợp nhất:** Đọc nhiều, ghi ít (Read-heavy, Write-light).

---

## 5. Cache và Memory-Based Storage (Bộ nhớ đệm)

**RAM** cung cấp tốc độ truy cập cực nhanh nhưng dữ liệu sẽ biến mất nếu mất điện. Do đó, các hệ thống này主要用于 (mainly used for) mục đích caching hoặc xử lý thời gian thực, không phải lưu trữ vĩnh viễn.

### Khi nào dùng?
Khi Data Engineer cần phục vụ dữ liệu với **latency cực thấp** hoặc giảm tải cho hệ thống backend.

### Các lựa chọn phổ biến

| Hệ thống | Đặc điểm | Phù hợp nhất |
| :--- | :--- | :--- |
| **Memcached** | Đơn giản, key-value, không persist (không ghi đĩa). | Cache kết quả truy vấn SQL, response API. Tối ưu hiệu suất thuần túy. |
| **Redis** | Hỗ trợ cấu trúc dữ liệu phức tạp (List, Set), có cơ chế persist (Snapshot/Journaling). | Dữ liệu cần độ tin cậy cao hơn, nhưng vẫn chấp nhận mất một lượng nhỏ dữ liệu (ví dụ: giỏ hàng, phiên đăng nhập). |

---

## 6. Hadoop Distributed File System (HDFS)

Trước đây, "Big Data" gần như đồng nghĩa với "Hadoop". HDFS dựa trên Google File System (GFS).

### Kiến trúc đặc trưng
*   **Tích hợp Compute & Storage:** Khác với Object Store (tách biệt), HDFS đặt cả lưu trữ và xử lý dữ liệu trên cùng các node (Data Locality).
*   **Phân mảnh (Block):** Chia tệp lớn thành các block nhỏ (ví dụ < 100MB).
*   **Phục hồi:** Sao chép (Replication) 3 bản sao mỗi block lên các node khác nhau.

### Tình trạng hiện tại: "Hadoop is dead?"
*   **Thực tế:** Hadoop không còn là công nghệ "hot" nhất. MapReduce thuần đã lỗi thời.
*   **Di sản:** HDFS vẫn sống sót và là nền tảng cho nhiều công cụ hiện đại (ví dụ: **Amazon EMR**, **Apache Spark** chạy trên HDFS).
*   **Quyết định:**
    *   **Doanh nghiệp lớn (On-premise):** Nếu đang duy trì cluster nghìn node, việc duy trì Hadoop vẫn hợp lý.
    *   **Doanh nghiệp nhỏ:** Nên cân nhắc di chuyển lên Cloud để giảm chi phí vận hành và phức tạp.

---

## 7. Streaming Storage (Lưu trữ luồng)

Dữ liệu streaming (như log, event stream) có vòng đời ngắn hơn, nhưng các hệ thống hiện đại cho phép lưu trữ dài hạn.

### Đặc điểm chính
*   **Retention:** Dữ liệu thường có thời hạn sử dụng (TTL).
*   **Replay:** Tính năng quan trọng cho phép đọc lại dữ liệu lịch sử trong một khoảng thời gian nhất định để xử lý lại (reprocess) hoặc chạy batch query.
*   **Các công cụ:** Apache Kafka, Amazon Kinesis, Apache Pulsar.

---

## 8. Tối ưu hóa Truy vấn: Từ Index đến Columnar & Partitioning

### Vấn đề với Index truyền thống
Trong cơ sở dữ liệu quan hệ (RDBMS), Index giúp tìm kiếm nhanh nhưng tốn tài nguyên và chậm khi quét lượng dữ liệu lớn (Full Table Scan).

### Sự trỗi dậy của Columnar Storage
*   **Cơ chế:** Lưu trữ dữ liệu theo cột (column) thay vì hàng (row).
*   **Lợi ích:**
    *   Chỉ đọc các cột cần thiết cho query (giảm IO).
    *   Nén dữ liệu hiệu quả (giá trị tương tự được đặt cạnh nhau).
*   **Hạn chế:** Kém hiệu quả cho giao dịch (OLTP), nhưng **xuất sắc** cho phân tích (OLAP).

### Tối ưu hóa thêm: Partitioning và Clustering
Để giảm thiểu dữ liệu quét (Data Pruning), ta áp dụng:

1.  **Partitioning (Phân vùng):** Chia bảng thành các phần con dựa trên trường (ví dụ: `Date`). Query chỉ quét các partition cần thiết.
2.  **Clustering (Sắp xếp):** Sắp xếp dữ liệu *bên trong* partition dựa trên các trường khác để tối ưu hóa join và filter.

### Ví dụ thực tế: Snowflake Micro-partitioning
Snowflake không partitioning theo cách truyền thống (chọn một cột cố định). Thay vào đó:
*   Nó tự động tạo các **Micro-partitions** (nhóm hàng 50-500MB).
*   Phân tích metadata để xác định các giá trị lặp lại (high cardinality).
*   **Tự động Pruning:** Nếu query lọc theo `WHERE created_date='2022-01-02'`, Snowflake bỏ qua hoàn toàn các micro-partition không chứa dữ liệu ngày này, dựa vào metadata mà không cần quét dữ liệu thực tế.

**Tóm lại:** Khi thiết kế hệ thống lưu trữ cho Analytics, hãy ưu tiên **Columnar Format** + **Partitioning** để tối ưu chi phí và tốc độ truy vấn.

---

