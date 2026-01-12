# Chapter 4.

Dưới đây là bản dịch và tổng hợp nội dung theo yêu cầu của bạn, được trình bày dưới dạng **Decision Guide** (Hướng dẫn ra quyết định) tập trung vào các khía cạnh kỹ thuật và chiến lược lưu trữ dữ liệu.

***

# Quyết định về Lưu trữ Dữ liệu (Data Storage Decision Guide)

Tài liệu này tóm tắt các xu hướng và khái niệm lớn trong lưu trữ dữ liệu, tập trung vào việc tối ưu hóa chi phí, quản lý vòng đời và kiến trúc lưu trữ.

## 1. Zero-Copy Cloning

**Zero-copy cloning** (nhân bản không sao chép) là một tính năng cho phép tạo một bản sao ảo của đối tượng (ví dụ: bảng dữ liệu) mà không cần sao chép vật lý dữ liệu cơ sở.

*   **Cơ chế hoạt động:** Hệ thống tạo các con trỏ mới trỏ đến tệp dữ liệu thô ban đầu. Các thay đổi đối với bản sao sẽ không ảnh hưởng đến bản gốc.
*   **Phân loại:**
    *   **Shallow Copy (Nhân bản nông):** Chia sẻ dữ liệu cơ sở. Rất nhanh và hiệu quả về chi phí.
    *   **Deep Copy (Nhân bản sâu):** Sao chép toàn bộ dữ liệu cơ sở. Chậm hơn và tốn kém hơn nhưng an toàn hơn.

#### Bảng so sánh Shallow Copy và Deep Copy

| Tính năng | Shallow Copy (Zero-Copy) | Deep Copy |
| :--- | :--- | :--- |
| **Cơ chế** | Tạo con trỏ mới, không di chuyển dữ liệu | Sao chép vật lý dữ liệu |
| **Tốc độ** | Tức thời (Instant) | Chậm (Phụ thuộc vào dung lượng) |
| **Chi phí** | Rất thấp | Cao |
| **Rủi ro** | Nếu xóa file gốc, bản sao có thể bị mất dữ liệu | An toàn, tách biệt hoàn toàn |
| **Ví dụ hệ thống** | Snowflake, BigQuery (Managed), Databricks | Databricks (tùy chọn), HDFS |

#### Khi nào nên dùng?
*   **Dùng Shallow Copy:** Khi cần tạo môi trường thử nghiệm (Dev/Test), phân tích nhanh mà không cần lưu giữ dữ liệu lâu dài.
*   **Dùng Deep Copy:** Khi dữ liệu cực kỳ quan trọng, cần đảm bảo sự tách biệt tuyệt đối để tránh rủi ro xóa nhầm dữ liệu gốc.

> **Cảnh báo:** Với các hệ thống Data Lake (như Databricks), kỹ sư dữ liệu cần cực kỳ thận trọng khi xóa file thô (raw files) vì nó có thể phá vỡ các bản sao đang dùng chung.

---

## 2. Vòng đời lưu trữ và nhiệt độ dữ liệu (Data Storage Lifecycle & Temperature)

Lưu trữ không chỉ là "để đó". Bạn cần quản lý dựa trên tần suất truy cập và giá trị của dữ liệu.

### Các cấp độ lưu trữ (Storage Tiers)

Chúng ta chia dữ liệu thành 3 "nhiệt độ" dựa trên tần suất truy cập:

#### A. Hot Data (Dữ liệu Nóng)
*   **Đặc điểm:** Truy cập tức thời hoặc liên tục.
*   **Lưu trữ:** SSD, Memory (RAM), Cache.
*   **Ưu điểm:** Tốc độ cực nhanh.
*   **Nhược điểm:** Chi phí lưu trữ cao nhất.
*   **Use Case:** Trang web chính, giỏ hàng, Query Results Cache (kết quả truy vấn được lưu tạm để tái sử dụng).

#### B. Warm Data (Dữ liệu Ấm)
*   **Đặc điểm:** Truy cập định kỳ (ví dụ: 1 lần/tháng).
*   **Lưu trữ:** Object Storage tiers (S3 Infrequent Access, Google Cloud Nearline).
*   **Ưu điểm:** Chi phí thấp hơn Hot.
*   **Nhược điểm:** Chi phí truy xuất (retrieval cost) cao hơn Hot một chút.
*   **Use Case:** Dữ liệu phân tích định kỳ, nhật ký hoạt động cũ.

#### C. Cold Data (Dữ liệu Lạnh)
*   **Đặc điểm:** Truy cập rất hiếm khi hoặc chỉ để lưu trữ đối chứng (Archival).
*   **Lưu trữ:** HDD, Tape, Cloud Archive (S3 Glacier).
*   **Ưu điểm:** Chi phí lưu trữ cực thấp.
*   **Nhược điểm:** Chi phí và thời gian truy xuất rất cao (có thể mất vài giờ hoặc ngày).
*   **Use Case:** Dữ liệu tuân thủ pháp luật (dữ liệu cũ), dữ liệu backup.

#### Quyết định chiến lược:
*   **Đừng lưu tất cả vào Hot:** Sẽ "đốt tiền" vô ích.
*   **Đừng lưu tất cả vào Cold:** Sẽ không thể truy xuất khi cần thiết kịp thời.
*   **Sử dụng Lifecycle Policy:** Tự động hóa việc chuyển dữ liệu từ Hot -> Warm -> Cold dựa trên độ tuổi và tần suất truy cập.

---

## 3. Quản lý Dữ liệu (Data Retention)

Đừng biến Data Lake thành Data Swamp (đầm lầy dữ liệu). Bạn cần trả lời câu hỏi: **"Nên giữ dữ liệu bao lâu?"**

#### Các yếu tố quyết định Retention Policy:

1.  **Giá trị (Value):**
    *   Dữ liệu này có dễ tạo lại không (Re-creatable)?
    *   Nếu mất, tác động đến downstream (người dùng cuối) như thế nào?
2.  **Thời gian (Time):**
    *   Dữ liệu mới thường có giá trị hơn.
    *   **TTL (Time To Live):** Cần đặt giới hạn thời gian sống cho dữ liệu trong bộ nhớ đệm (Cache) để tránh tràn bộ nhớ.
3.  **Tuân thủ (Compliance):**
    *   Các quy định như HIPAA, PCI yêu cầu giữ dữ liệu trong X năm.
    *   Các quy định khác có thể yêu cầu **xóa** dữ liệu sau Y năm (Right to be Forgotten).
4.  **Chi phí (Cost):**
    *   Cân đối giữa chi phí lưu trữ và giá trị của dữ liệu đó mang lại (ROI).

---

## 4. Kiến trúc Lưu trữ: Đơn tenant vs Đa tenant (Single vs Multitenant)

Đây là quyết định về cách tổ chức dữ liệu của nhiều người dùng (khách hàng) trên hệ thống.

#### Single-Tenant Storage (Lưu trữ Đơn tenant)
*   **Cấu trúc:** Mỗi người dùng/nhóm/công ty có một cơ sở dữ liệu (Database) hoặc bucket tách biệt hoàn toàn.
*   **Ưu điểm:**
    *   **Bảo mật & Cách ly:** Tuyệt đối không lo rò rỉ dữ liệu giữa các khách hàng.
    *   **Linh hoạt:** Có thể tùy chỉnh Schema (cấu trúc bảng) riêng cho từng khách hàng.
*   **Nhược điểm:**
    *   Chi phí cao hơn (nhiều DB, nhiều tài nguyên).
    *   Khó khăn khi cần tổng hợp dữ liệu giữa các khách hàng (Unified View).
*   **Khi nào dùng:** Khi yêu cầu bảo mật cao (ví dụ: ngân hàng, y tế), hoặc khách hàng yêu cầu tùy chỉnh sâu.

#### Multitenant Storage (Lưu trữ Đa tenant)
*   **Cấu trúc:** Nhiều người dùng chung một Database, phân biệt dữ liệu bằng cột `tenant_id` hoặc schema riêng.
*   **Ưu điểm:**
    *   Chi phí thấp, hiệu quả tài nguyên cao.
    *   Dễ dàng quản lý và scale.
    *   Dễ dàng phân tích chéo (Cross-tenant analytics).
*   **Nhược điểm:**
    *   Rủi ro rò rỉ dữ liệu nếu lỗi phân quyền (một khách hàng thấy dữ liệu của khách hàng khác).
    *   Schema phải đồng nhất (Uniform).
*   **Khi nào dùng:** Ứng dụng SaaS phổ thông, người dùng cá nhân, khi cần tối ưu chi phí.

---

## 5. Các yếu tố Ngầm (Undercurrents) trong Lưu trữ

Lưu trữ là trung tâm, vì vậy các yếu tố này phải được đặt lên hàng đầu.

### A. Bảo mật (Security)
*   **Nguyên tắc:** **Least Privilege** (Quyền hạn tối thiểu).
*   **Hành động:** Đừng cấp quyền truy cập Database đầy đủ cho tất cả kỹ sư.
*   **Tính năng:** Sử dụng kiểm soát truy cập theo cột (Column-level), hàng (Row-level) và ô (Cell-level) để ẩn dữ liệu nhạy cảm.

### B. Quản lý dữ liệu (Data Management)
*   **Metadata & Data Catalog:** Bạn không thể quản lý những gì bạn không biết. Cần Catalog để người dùng khám phá dữ liệu.
*   **Data Lineage:** Theo dõi nguồn gốc dữ liệu để sửa lỗi nhanh hơn.
*   **Data Versioning:** Giữ lại các phiên bản dữ liệu cũ (giống Git cho code) để debug khi model hoặc report bị lỗi.

### C. Quyền riêng tư (Privacy)
*   Tuân thủ GDPR.
*   Chuẩn bị sẵn quy trình xóa dữ liệu theo yêu cầu (Data Deletion Request).
*   Sử dụng **Anonymization** (Giấu tên) và **Masking** (Che chắn) dữ liệu nhạy cảm.

### D. DataOps & Quan sát (Monitoring)
*   **FinOps:** Quản lý chi phí lưu trữ (đây là trách nhiệm của Data Engineer).
*   **Quan sát dữ liệu (Data Observability):** Đừng chỉ monitor hệ thống (disk full?), hãy monitor dữ liệu (dữ liệu có bị hỏng? có bất thường không?).
*   **Anomaly Detection:** Tự động phát hiện các thay đổi bất thường trong dữ liệu để ngăn chặn lỗi lan truyền.

---

