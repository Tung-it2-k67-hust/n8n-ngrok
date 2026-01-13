# Chapter 3, and we will revisit them here.

Dưới đây là bản dịch và tổng hợp nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide** (Hướng dẫn ra quyết định) tập trung vào các khía cạnh chuyên môn của Data Engineering.

***

# Các Khái niệm Trữ liệu (Storage Abstractions) trong Kỹ thuật Dữ liệu

Tài liệu này tóm tắt các khái niệm lưu trữ cốt lõi trong vòng đời dữ liệu, tập trung vào các mô hình hỗ trợ khoa học dữ liệu, phân tích và báo cáo.

## 1. Các yếu tố quyết định khi lựa chọn Storage Abstraction

Trước khi chọn công nghệ, kỹ sư dữ liệu cần cân nhắc các yếu tố sau:

*   **Mục đích và Use case:** Dữ liệu dùng để làm gì? (Báo cáo, phân tích thời gian thực, dữ liệu thô...).
*   **Mẫu cập nhật (Update patterns):** Hệ thống có tối ưu cho cập nhật hàng loạt (*bulk updates*), chèn luồng (*streaming inserts*) hay cập nhật/chèn kết hợp (*upserts*)?
*   **Chi phí (Cost):** Chi phí trực tiếp/gián tiếp, thời gian để tạo ra giá trị (Time to value), và chi phí cơ hội.
*   **Tách biệt Storage và Compute:** Đây là xu hướng chủ đạo, giúp tối ưu chi phí và linh hoạt quy mô.

---

## 2. Các mô hình Storage chính

### Data Warehouse (Kho dữ liệu)

*   **Là gì?** Nền tảng kiến trúc OLAP chuẩn, dùng để tập trung dữ liệu đã được xử lý.
*   **Tại sao dùng?**
    *   Tối ưu cho các truy vấn phức tạp, báo cáo định kỳ.
    *   Đảm bảo chất lượng dữ liệu (Data Quality) và cấu trúc rõ ràng (Schema).
*   **Khi nào dùng?** Khi cần độ tin cậy cao, dữ liệu có cấu trúc và cần truy vấn nhanh trên các tập dữ liệu quy mô lớn.
*   **Ưu điểm:** Hiệu suất cao, quản lý schema chặt chẽ.
*   **Nhược điểm:** Khó xử lý dữ liệu thô (hình ảnh, video, audio không cấu trúc); chi phí/lich sử phần cứng truyền thống (trước khi lên Cloud).

### Data Lake (Hồ dữ liệu)

*   **Là gì?** Kho lưu trữ dữ liệu thô (raw, unprocessed) với dung lượng lớn, giá rẻ.
*   **Tại sao dùng?**
    *   Lưu trữ mọi loại dữ liệu không cấu trúc hoặc bán cấu trúc.
    *   Giữ lại dữ liệu thô để phục vụ cho các mục đích trong tương lai.
*   **Khi nào dùng?** Khi cần lưu trữ lượng dữ liệu khổng lồ với chi phí thấp, hoặc khi chưa biết chính xác cách sử dụng dữ liệu trong tương lai.
*   **Ưu điểm:** Linh hoạt, chi phí lưu trữ thấp (dựa trên Hadoop hoặc Object Storage).
*   **Nhược điểm:** Dễ trở thành "Data Swamp" (bãi lầy dữ liệu) nếu không có quản lý; thiếu các tính năng quản lý bản ghi (update/delete) và schema management của MPP systems.

### Data Lakehouse

*   **Là gì?** Kiến trúc lai, kết hợp tính năng của Data Warehouse và Data Lake.
*   **Tại sao dùng?**
    *   Lưu trữ dữ liệu thô dạng Object Storage (như Lake).
    *   Thêm lớp quản lý metadata, hỗ trợ update/delete, schema management (như Warehouse).
*   **Khi nào dùng?** Khi cần sự linh hoạt của Lake nhưng vẫn muốn có trải nghiệm kỹ thuật mạnh mẽ, hỗ trợ transaction (ví dụ: Delta Lake, Apache Iceberg).
*   **Ưu điểm:** **Tính tương tác cao (Interoperability)** giữa các công cụ; dễ dàng trao đổi dữ liệu ở định dạng mở; che giấu sự phức tạp của việc quản lý file lưu trữ.
*   **Nhược điểm:** Công nghệ còn non trẻ, đang phát triển nhanh chóng.

### Data Platforms (Nền tảng dữ liệu)

*   **Là gì?** Các nhà cung cấp tạo ra hệ sinh thái công cụ tích hợp sâu với lớp lưu trữ cốt lõi.
*   **Tại sao dùng?** Để đơn giản hóa quy trình Data Engineering.
*   **Khi nào dùng?** Khi doanh nghiệp muốn một giải pháp "tất cả trong một" (All-in-one).
*   **Lưu ý:** Xu hướng này tạo ra sự **Vendor Lock-in** (phụ thuộc vào nhà cung cấp).

---

## 3. Kiến trúc lưu trữ Stream-to-Batch

Kiến trúc này tương tự Lambda Architecture, nơi dữ liệu từ luồng (Streaming) được ghi ra nhiều consumer:

1.  **Real-time consumer:** Xử lý thống kê tức thì.
2.  **Batch consumer:** Ghi dữ liệu vào lưu trữ dài hạn (ví dụ: AWS Kinesis Firehose ghi vào S3, BigQuery ghi vào Columnar Object Storage).
*   **Lợi ích:** Cung cấp view gần như thời gian thực (nearly real-time) kết hợp với khả năng query dữ liệu lịch sử.

---

## 4. Các Xu hướng và Khái niệm Nâng cao

### Data Catalog (Thư viện dữ liệu)

*   **Vai trò:** Kho metadata tập trung, giúp khám phá dữ liệu (Data Discoverability).
*   **Cách tiếp cận:**
    *   *Catalog Application Integration:* Ứng dụng tích hợp trực tiếp qua API.
    *   *Automated Scanning:* Quét tự động để suy luận metadata (sensitive data, key relationships).
    *   *Data Portal:* Giao diện web cho người dùng tìm kiếm và tương tác (Wiki, Social layer).
*   **Lợi ích:** Giúp các bộ phận (Business, Data Science, Engineering) giao tiếp và hợp tác hiệu quả.

### Data Sharing (Chia sẻ dữ liệu)

*   **Là gì?** Cho phép chia sẻ dữ liệu cụ thể với các thực thể bên ngoài hoặc nội bộ với quyền kiểm soát chặt chẽ.
*   **Lợi ích:** Hợp tác giữa các doanh nghiệp đối tác (ví dụ: Ad-tech company chia sẻ data với khách hàng).
*   **Rủi ro:** An ninh mạng, rò rỉ dữ liệu.

### Schema (Lược đồ dữ liệu)

Có hai mô hình Schema chính:

| Mô hình | **Schema on Write** | **Schema on Read** |
| :--- | :--- | :--- |
| **Định nghĩa** | Áp dụng Schema khi ghi dữ liệu vào. Dữ liệu phải tuân thủ cấu trúc. | Schema được xác định động khi đọc dữ liệu. |
| **Ưu điểm** | Đảm bảo tiêu chuẩn dữ liệu, dễ tiêu thụ sau này. | Linh hoạt cao, ghi được mọi loại dữ liệu thô. |
| **Nhược điểm** | Khó thay đổi cấu trúc nếu dữ liệu đã có sẵn. | Khó khăn hơn trong việc tiêu thụ dữ liệu về sau. |
| **Định dạng gợi ý** | Parquet, JSON (có cấu trúc). | CSV (không khuyến khích do dễ sai lệch). |

### Tách biệt Compute và Storage (Separation of Compute from Storage)

Đây là xu hướng then chốt trong kỷ nguyên Cloud.

*   **Colocation (Tồn tại cùng nhau):**
    *   *Ưu điểm:* Tốc độ cao, độ trễ thấp (đọc/ghi trực tiếp vào đĩa).
    *   *Ví dụ:* HDFS, MapReduce (đưa job đến gần dữ liệu).
*   **Separation (Tách biệt):**
    *   *Lý do:* **Ephemerality (Tính nhất thời)** và **Scalability (Mở rộng)**. Bạn có thể bật/tắt cluster khổng lồ tùy theo nhu cầu (Pay-as-you-go).
    *   *Độ bền (Durability):* Object Storage (như S3) sao lưu dữ liệu qua nhiều Zone, đảm bảo an toàn dữ liệu cao.
*   **Hybrid (Lai):** Kết hợp cả hai để tối ưu hiệu năng.
    *   *Multitier caching:* Dùng Object Storage lâu dài, nhưng dùng Local Storage tạm thời trong quá trình query.
    *   *Ví dụ thực tiễn:*
        *   **AWS EMR:** Dùng SSD local (HDFS) để xử lý trung gian, ghi kết quả cuối về S3.
        *   **Apache Spark:** Dùng RAM (In-memory) và Ephemeral storage để xử lý nhanh.
        *   **Apache Druid:** Dùng SSD cho live data và Object Store cho durability.
        *   **Hybrid Object Storage (BigQuery/S3 Select):** Lọc dữ liệu trực tiếp tại lớp lưu trữ trước khi truyền qua mạng, tiết kiệm băng thông.

---

