# Phân tích chi tiết: 7_apache_spark.pdf

Chào bạn, tôi là một chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết về nội dung slide "Apache Spark" dựa trên tài liệu bạn cung cấp, được trình bày một cách chuyên nghiệp và chi tiết theo yêu cầu.

---

# Apache Spark: Nền tảng Xử lý Dữ liệu Lớn Hợp nhất

Apache Spark là một framework mã nguồn mở mạnh mẽ, được thiết kế để xử lý dữ liệu lớn với tốc độ cực nhanh. Nó được xem là sự kế thừa và cải tiến của mô hình MapReduce, giải quyết các vấn đề về hiệu năng và tính linh hoạt.

## 1. Phân tích vấn đề của MapReduce

Theo tài liệu slide, nhược điểm lớn nhất của MapReduce trong các tác vụ phức tạp là vấn đề **I/O (Input/Output)**.

### Khái niệm: "Iterative Jobs" (Các tác vụ lặp lại)

*   **Giải thích:** Trong machine learning hoặc xử lý đồ thị, chúng ta thường cần chạy một thuật toán nhiều lần (vòng lặp) trên cùng một tập dữ liệu để tối ưu hóa kết quả (ví dụ: Gradient Descent).
*   **Vấn đề với MapReduce:** MapReduce được thiết kế cho các tác vụ độc lập. Mỗi lần chạy (job) MapReduce đều phải đọc dữ liệu từ **HDFS (Hadoop Distributed File System)** và ghi kết quả trở lại đĩa cứng. Việc này tạo ra độ trễ lớn do tốc độ đọc/ghi đĩa cứng chậm.

### So sánh tốc độ I/O (Theo Slide)

Tài liệu cung cấp bảng so sánh trực quan về tốc độ và độ trễ giữa các thành phần phần cứng:

| Thành phần | Tốc độ Truyền tải (Throughput) | Độ trễ Truy cập (Latency) | Chi phí (Cost) |
| :--- | :--- | :--- | :--- |
| **Network (Cross-Rack)** | 1 Gb/s (~125 MB/s) | - | - |
| **Network (Intra-Rack)** | 10 Gb/s | - | - |
| **Disk (Random Access)** | - | 3-12 ms | $0.025 per GB |
| **RAM (Random Access)** | 600 MB/s (Aggregate) | 0.1 ms | $0.35 per GB |

*   **Nhận định:** RAM nhanh hơn Disk khoảng **100 lần** về độ trễ (Latency) và có tốc độ truyền tải cao hơn hẳn so với việc truy cập ngẫu nhiên trên đĩa cứng.
*   **Lời giải của Spark:** Thay vì phụ thuộc vào đĩa cứng, Spark sử dụng **RAM** làm lưu trữ chính, giúp tăng tốc độ xử lý các tác vụ lặp lại một cách đột biến.

---

## 2. Các khái niệm và giải pháp của Apache Spark

Spark ra đời để giải quyết các bài toán mà MapReduce gặp khó khăn, đặc biệt là trong các môi trường cần sự tương tác và lặp lại.

### Khái niệm chính: In-Memory Processing (Xử lý trong bộ nhớ)

*   **Giải thích:** Spark lưu trữ dữ liệu trung gian (intermediate data) vào RAM, thay vì ghi ra đĩa cứng như MapReduce.
*   **Ưu điểm:** Giảm đáng kể thời gian I/O, cho phép các thuật toán truy cập dữ liệu gần như tức thời.

### Khái niệm chính: Unified Platform (Nền tảng Hợp nhất)

*   **Giải thích:** Spark cung cấp một API duy nhất cho nhiều loại tác vụ khác nhau:
    *   **Batch Processing:** Xử lý hàng loạt (thay thế MapReduce).
    *   **Streaming:** Xử lý dữ liệu thời gian thực.
    *   **Interactive Queries:** Truy vấn tương tác (SQL).
    *   **Machine Learning:** Học máy.

---

## 3. Code Mẫu và Hướng dẫn Sử dụng

Dưới đây là các ví dụ thực tế minh họa sự khác biệt và cách sử dụng Spark.

### Ví dụ 1: Bài toán Lặp lại (Iterative Algorithm) - Machine Learning

Giả sử chúng ta muốn tìm giá trị tối ưu của một biến `x` bằng thuật toán Gradient Descent, cần chạy 100 vòng lặp.

#### A. Mã giả (Pseudo-code) của MapReduce (Cũ - Chậm)
```text
For i in 1 to 100:
    1. Đọc dữ liệu từ HDFS.
    2. Map: Tính toán gradient.
    3. Reduce: Cập nhật giá trị x.
    4. Ghi kết quả ra HDFS (I/O chậm).
```

#### B. Code Mẫu Apache Spark (Python/PySpark) - Mới - Nhanh

Trong Spark, dữ liệu được load một lần vào **RDD (Resilient Distributed Dataset)** hoặc **DataFrame** và giữ trong RAM.

```python
from pyspark import SparkContext, SparkConf
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionWithSGD

# 1. Cấu hình Spark (Sử dụng Memory)
conf = SparkConf().setAppName("IterativeML").setMaster("local[*]")
sc = SparkContext(conf=conf)

# 2. Load dữ liệu một lần (Đọc từ HDFS/HDFS)
# Dữ liệu này sẽ được giữ trong RAM
data = sc.textFile("hdfs://data/train_data.txt") \
    .map(parsePoint) # Hàm parse dữ liệu tùy chỉnh

# 3. Huấn luyện mô hình với nhiều vòng lặp (Iterations)
# Spark tự động xử lý vòng lặp trong bộ nhớ, không cần ghi ra đĩa
model = LogisticRegressionWithSGD.train(data, iterations=100, step=0.1)

# 4. Dự đoán
labelsAndPreds = data.map(lambda p: (p.label, model.predict(p.features)))
print("Độ chính xác:", labelsAndPreds.filter(lambda vp: vp[0] == vp[1]).count() / float(data.count()))
```

**Hướng dẫn sử dụng:**
*   **Khi nào sử dụng?** Khi bạn cần chạy các thuật toán Machine Learning (MLlib), xử lý đồ thị (GraphX) hoặc các phép tính lặp lại trên dữ liệu lớn.
*   **Cách dùng:** Tải dữ liệu vào Spark Context một lần, thực hiện các phép biến đổi (Transformation) và hành động (Action) liên tục mà không cần gọi I/O giữa các bước.

---

### Ví dụ 2: Interactive Data Mining (Khai phá dữ liệu Tương tác)

Spark cho phép các nhà khoa học dữ liệu chạy các truy vấn và phân tích lặp đi lặp lại một cách nhanh chóng để khám phá thông tin chi tiết (Insights).

#### Code Mẫu: Phân tích Log bằng Spark SQL

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

# Khởi tạo Spark Session (Cần thiết cho SQL)
spark = SparkSession.builder.appName("InteractiveMining").getOrCreate()

# Đọc dữ liệu log (JSON/CSV)
df = spark.read.json("hdfs://logs/server_logs.json")

# 1. Truy vấn đầu tiên: Lấy top 5 lỗi phổ biến nhất
top_errors = df.filter(col("status") == 500) \
               .groupBy("error_code") \
               .agg(count("*").alias("total_count")) \
               .orderBy(col("total_count").desc()) \
               .limit(5)

top_errors.show() # Hiển thị kết quả ngay lập tức

# 2. Truy vấn thứ hai (Tương tác): Phân tích theo giờ mà không cần reload dữ liệu
# (Dữ liệu df vẫn nằm trong RAM)
hourly_traffic = df.groupBy(col("timestamp").substr(1, 13).alias("hour")) \
                   .agg(count("*").alias("requests")) \
                   .orderBy(col("requests").desc())

hourly_traffic.show()
```

**Hướng dẫn sử dụng:**
*   **Khi nào sử dụng?** Phù hợp cho các Data Analyst cần khám phá dữ liệu, chạy nhiều truy vấn khác nhau để tìm trend, hoặc làm việc với Jupyter Notebook.
*   **Cách dùng:** Sử dụng **Spark SQL** hoặc **DataFrames API**. Dữ liệu được cache (lưu vào RAM) để các truy vấn tiếp theo chạy gần như tức thì.

---

## 4. Tóm tắt Ưu & Nhược điểm của Apache Spark

| Tiêu chí | Chi tiết |
| :--- | :--- |
| **Ưu điểm (Pros)** | **Tốc độ:** Nhanh hơn MapReduce 10-100 lần nhờ xử lý trong RAM.<br>**Tính linh hoạt:** Hỗ trợ Batch, Streaming, SQL, ML trong một framework.<br>**Dễ sử dụng:** Cung cấp API cao cấp cho Java, Scala, Python, R.<br>**Tolerance:** Chịu lỗi tốt (Fault Tolerance) thông qua RDD lineage. |
| **Nhược điểm (Cons)** | **Bộ nhớ RAM:** Đòi hỏi tài nguyên phần cứng (RAM) lớn hơn MapReduce.<br>**Quản lý bộ nhớ:** Nếu không cẩn thận, dễ gây ra lỗi OutOfMemory.<br>**Chi phí:** Chi phí infrastructure cao hơn nếu so sánh chỉ xét về tài nguyên CPU/RAM. |

---

## 5. Ví dụ Thực tế trong Industry

1.  **Netflix:**
    *   **Sử dụng:** Spark Streaming để xử lý dữ liệu log người dùng xem phim theo thời gian thực.
    *   **Mục đích:** Cập nhật "Top 10 phim thịnh hành" ngay lập tức và đề xuất phim (Recommendation Engine) dựa trên hành vi gần nhất của người dùng.

2.  **Uber:**
    *   **Sử dụng:** Spark (Batch & Streaming) để tính toán giá cước (Surge Pricing).
    *   **Mục đích:** Phân tích lượng xe và nhu cầu theo thời gian thực để điều chỉnh giá cước (Dynamic Pricing).

3.  **Trung tâm Dữ liệu Y tế (Healthcare):**
    *   **Sử dụng:** Spark MLlib.
    *   **Mục đích:** Chạy các thuật toán lặp lại (Iterative Algorithms) để phát hiện sớm bệnh tật dựa trên dữ liệu lịch sử bệnh án khổng lồ, điều mà MapReduce làm rất chậm.

---

Chào bạn, tôi là chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết và trình bày lại nội dung từ slide "7_apache_spark.pdf" theo yêu cầu của bạn.

---

# Apache Spark: Phân tích & Hướng dẫn Chi tiết

Apache Spark là một nền tảng điện toán song song và phân tán cho dữ liệu lớn (Big Data), được thiết kế để mang lại hiệu suất cao và sự linh hoạt. Nó được xem là một bản nâng cấp của Hadoop MapReduce, giải quyết các vấn đề về tốc độ và khả năng xử lý đa dạng workload.

## 1. Kiến trúc và Ecosystem của Spark

Spark cung cấp một nền tảng xử lý dữ liệu hợp nhất (Unified Platform) cho phép xử lý nhiều loại dữ liệu và workload khác nhau trên cùng một engine.

### 1.1. Các thành phần chính (Components)

Hệ sinh thái Spark bao gồm các module chính:

*   **Spark Core**: Là phần nền tảng cốt lõi, chịu trách nhiệm quản lý bộ nhớ, phân bổ tài nguyên, và thực thi các tác vụ. Nó cung cấp **RDD API** (Resilient Distributed Dataset) - cấu trúc dữ liệu cơ bản của Spark.
*   **Spark SQL**: Dùng để xử lý dữ liệu có cấu trúc (structured data). Nó cho phép chạy các truy vấn SQL hoặc sử dụng DataFrame API để xử lý dữ liệu.
*   **Spark Streaming**: Xử lý dữ liệu thời gian thực (real-time streaming data) bằng cách chia dữ liệu thành các batch nhỏ.
*   **MLlib**: Thư viện Machine Learning cung cấp các thuật toán học máy phổ biến.
*   **GraphX**: Thư viện xử lý dữ liệu dạng đồ thị (graph processing).

### 1.2. Mô hình Hoạt động

Spark có thể chạy trên nhiều môi trường quản lý tài nguyên (Cluster Managers) khác nhau:
*   **Standalone**: Mô hình đơn giản nhất, tích hợp sẵn trong Spark.
*   **YARN**: Môi trường quản lý tài nguyên của Hadoop (Hadoop YARN).
*   **Mesos**: Một cluster manager khác.
*   **Kubernetes**: Quản lý container phổ biến hiện nay.

### 1.3. Ví dụ Code: Khởi tạo SparkSession

Đây là bước đầu tiên để bắt đầu làm việc với Spark (Python).

```python
from pyspark.sql import SparkSession

# Khởi tạo một SparkSession
spark = SparkSession.builder \
    .appName("IntroductionToSpark") \
    .master("local[*]") \
    .getOrCreate()

# Kiểm tra Spark UI (Web Interface)
print("Spark UI đang chạy tại: http://localhost:4040")

# Tạo một DataFrame đơn giản
data = [("Alice", 34), ("Bob", 45), ("Charlie", 28)]
columns = ["Name", "Age"]
df = spark.createDataFrame(data, columns)

df.show()
```

---

## 2. So sánh Spark và MapReduce (Hadoop)

Đây là phần quan trọng để hiểu tại sao Spark lại trở nên phổ biến thay thế cho MapReduce truyền thống.

### 2.1. Bảng so sánh chi tiết

| Đặc điểm | Apache Hadoop MapReduce | Apache Spark |
| :--- | :--- | :--- |
| **Lưu trữ (Storage)** | Chỉ sử dụng **HDD** (Disk). Ghi dữ liệu trung gian xuống ổ đĩa sau mỗi tác vụ. | **In-Memory Computing**: Sử dụng **Bộ nhớ trong (RAM)** làm chủ yếu, có thể fallback về HDD nếu bộ nhớ không đủ. |
| **Operations** | Chỉ hỗ trợ 2 thao tác cơ bản: **Map** và **Reduce**. | Hỗ trợ nhiều thao tác biến đổi (**Transformations**) và hành động (**Actions**) linh hoạt (filter, join, groupBy, map, reduce, v.v.). |
| **Execution Model** | Xử lý theo khối (**Batch processing**) thuần túy. | Xử lý theo khối (**Batch**), tương tác (**Interactive**), và luồng (**Streaming**). |
| **Ngôn ngữ** | Chủ yếu **Java**. | **Scala**, **Java**, **Python**, **R**. |

### 2.2. Giải thích chi tiết

*   **In-Memory vs Disk**: MapReduce ghi dữ liệu trung gian ra đĩa cứng sau mỗi giai đoạn (Map hoặc Reduce), dẫn đến độ trễ lớn (I/O overhead). Spark lưu dữ liệu trung gian trong RAM, giúp tốc độ nhanh hơn tới 100 lần đối với các tác vụ truy vấn hoặc phân tích phức tạp.
*   **Tính linh hoạt**: MapReduce yêu cầu người dùng phải viết các hàm Map và Reduce rõ ràng. Spark cho phép thực hiện chuỗi các phép biến đổi (Pipeline) một cách trực quan hơn.

---

## 3. Hiệu năng: Spark vs MapReduce

Theo tài liệu tham khảo từ Databricks (databricks.com/blog/2014/10/10/spark-petabyte-sort.html), Spark đã chứng minh được hiệu năng vượt trội.

*   **Bài toán Sort (PetaByte Sort)**: Spark đã thực hiện sắp xếp 1 PB dữ liệu nhanh hơn 3 lần so với Hadoop MapReduce trên cùng một cụm (cluster).
*   **Tốc độ**: Đối với các tác vụ **Iterative Algorithms** (thuật toán lặp lại như trong Machine Learning), Spark nhanh hơn MapReduce hàng chục đến hàng trăm lần do không cần tải lại dữ liệu từ đĩa ở mỗi vòng lặp.

---

## 4. Giao diện Lệnh Tương tác (Interactive CLI)

Slide đề cập đến giao diện dòng lệnh cho phép người dùng tương tác trực tiếp với Spark bằng **Scala**, **Python**, và **R**.

*   **Công cụ**: `spark-shell` (dùng Scala), `pyspark` (dùng Python), `sparkR` (dùng R).
*   **Cách sử dụng**: Bạn mở terminal, gõ lệnh, và môi trường sẽ khởi tạo một Spark Context hoặc Session. Bạn có thể viết code và thực thi ngay lập tức mà không cần biên dịch (REPL - Read-Eval-Print Loop).

**Ví dụ Shell Script: Chạy một tác vụ Spark từ dòng lệnh**

```bash
# Chạy một file script Python bằng spark-submit
# Đây là cách triển khai thực tế trong production
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --executor-memory 4G \
  --num-executors 10 \
  /path/to/your_script.py
```

---

## 5. Ví dụ Thực tế trong Công nghiệp

### Use Case 1: Real-time Fraud Detection (Phát hiện gian lận thẻ tín dụng)
*   **Công nghệ**: **Spark Streaming**.
*   **Cách dùng**: Hệ thống nhận hàng nghìn giao dịch mỗi giây. Spark Streaming nhận dữ liệu từ Kafka, xử lý để phát hiện các mẫu giao dịch bất thường (ví dụ: chi tiêu ở hai quốc gia cùng lúc), và gửi cảnh báo ngay lập tức.
*   **Ưu điểm**: Khả năng xử lý thời gian thực và dung sai lỗi (fault tolerance).

### Use Case 2: Recommendation System (Hệ thống đề xuất)
*   **Công nghệ**: **Spark MLlib**.
*   **Cách dùng**: Phân tích lịch sử mua hàng của hàng triệu người dùng để tìm ra các quy luật (Collaborative Filtering). Ví dụ: "Những người mua sản phẩm A cũng thường mua sản phẩm B".
*   **Ưu điểm**: Xử lý dữ liệu thô (RDD/DataFrame) và huấn luyện model ngay trên nền tảng phân tán.

### Use Case 3: ETL và Phân tích Kinh doanh (Business Intelligence)
*   **Công nghệ**: **Spark SQL**.
*   **Cách dùng**: Trích xuất dữ liệu từ các nguồn (Data Sources) như HDFS, Hive, Cassandra. Biến đổi dữ liệu thô thành dữ liệu tổng hợp, sau đó load vào Data Warehouse (như Redshift hoặc Snowflake) để báo cáo.
*   **Ưu điểm**: SQL interface dễ sử dụng cho analyst, tốc độ nhanh giúp giảm thời gian chờ đợi báo cáo.

---

## 6. Tóm tắt Ưu & Nhược điểm của Apache Spark

| Ưu điểm (Pros) | Nhược điểm (Cons) |
| :--- | :--- |
| **Tốc độ cao**: In-memory processing giúp xử lý nhanh hơn MapReduce. | **Chi phí bộ nhớ**: Cần RAM lớn, chi phí infrastructure cao hơn MapReduce. |
| **Đa ngôn ngữ**: Hỗ trợ Python, Scala, Java, R. | **Complexity**: Cấu hình và tối ưu hóa Spark đòi hỏi kiến thức chuyên sâu. |
| **Unified Platform**: Xử lý batch, streaming, ML, graph trên cùng một nền tảng. | **Small Data**: Không hiệu quả bằng các công cụ truyền thống (như Pandas) nếu xử lý dữ liệu nhỏ (dưới 1GB). |
| **Tính linh hoạt**: Dễ dàng debug và phát triển. | |

---

**Kết luận**: Apache Spark là công cụ bắt buộc phải biết trong ngành Big Data hiện nay, đặc biệt là khi cần xử lý dữ liệu lớn với tốc độ cao và đa dạng các loại tác vụ.

---

Chào bạn, tôi là một chuyên gia về Big Data và Hệ thống Phân tán. Dựa trên tài liệu slide "7_apache_spark.pdf" bạn cung cấp, tôi sẽ phân tích và trình bày lại nội dung một cách chi tiết, chuyên sâu dưới dạng Markdown.

---

# Apache Spark: Kiến trúc và Khái niệm Nền tảng

Tài liệu này cung cấp cái nhìn tổng quan về cách Apache Spark thực thi chương trình và cấu trúc dữ liệu cơ bản của nó: **RDD (Resilient Distributed Dataset)**.

## 1. Kiến trúc Thực thi (Execution Architecture)

Spark hoạt động theo mô hình **Client-Server** (hoặc Master-Slave) phân tán. Khi một chương trình Spark được khởi chạy, nó bao gồm các thành phần chính sau:

### Các thành phần chính:
*   **Driver Program**: Đây là "bộ não" của ứng dụng Spark. Nó chạy trên một máy duy nhất (có thể là máy của người dùng hoặc một node Master). Driver Program chịu trách nhiệm:
    *   Tạo **SparkContext** (đối tượng chính để kết nối với cluster).
    *   Phân tích và lập kế hoạch thực thi (DAG - Directed Acyclic Graph).
    *   Phân bổ công việc cho các Worker node.
*   **Cluster Manager**: Hệ thống quản lý tài nguyên (như YARN, Mesos, hoặc Standalone) điều phối việc cấp phát tài nguyên cho các Executor.
*   **Worker Node**: Các máy tính trong cluster (máy trạm) chứa các Executor.
*   **Executor**: Các tiến trình chạy trên Worker Node, chịu trách nhiệm thực thi các tác vụ (task) được giao từ Driver. Chúng lưu trữ dữ liệu và kết quả tính toán.

### Sơ đồ luồng thực thi:
```text
[Driver Program] --(Yêu cầu tài nguyên)--> [Cluster Manager]
      |
      +--(Gửi Task)--> [Worker Machine 1 (Executor)]
      |                [Worker Machine 2 (Executor)]
      +--(Gửi Task)--> [Worker Machine 3 (Executor)]
```

---

## 2. Resilient Distributed Dataset (RDD)

**RDD** là khái niệm cốt lõi của Spark. Nó là một tập hợp dữ liệu phân vùng, không thể thay đổi (immutable) và được phân tán trên các node trong cluster.

### Định nghĩa & Đặc điểm:
*   **Cấu trúc song song và chịu lỗi (Fault-tolerant, parallel data structures)**: Dữ liệu được chia thành các phân vùng (partition) và xử lý song song trên nhiều Executor. Nếu một node bị lỗi, Spark có thể tái tạo dữ liệu bị mất từ các nguồn ban đầu.
*   **Lưu trữ trung gian trong bộ nhớ (Intermediate results in memory)**: Spark ưu tiên lưu dữ liệu trong RAM để tăng tốc độ truy cập và tính toán, khác biệt lớn so với Hadoop MapReduce (phải ghi xuống đĩa).
*   **Thao tác coarse-grained (thô)**: RDD được tối ưu cho các biến đổi hàng loạt (như `map`, `filter`, `join`) tác động lên nhiều bản ghi cùng lúc, thay vì các thao tác cập nhật chi tiết (fine-grained updates) từng dòng một.

### Khả năng tự phục hồi (Fault Tolerance):
RDD có khả năng tự động tái tạo lại khi bị lỗi. Điều này được thực hiện thông qua **Lineage Graph** (đồ thị dòng dõi). Nếu một phân vùng RDD bị mất, Spark sẽ biết cách tái tạo nó bằng cách áp dụng lại các phép biến đổi (transformations) từ nguồn dữ liệu ban đầu.

---

## 3. Phân vùng và Song song hóa (Partitioning & Parallelism)

Để khai thác sức mạnh của các hệ thống phân tán, RDD được chia thành các **Partition**.

### Nguyên lý hoạt động:
*   Dữ liệu (ví dụ: `item-1` đến `item-25`) được chia thành các nhóm nhỏ (Partition).
*   Mỗi Partition được xử lý bởi một **Task** trên một **Executor**.
*   Các Executor chạy song song trên các Worker Machine khác nhau.

**Sơ đồ phân vùng:**
```text
[Partition 1] -> [Worker 1 (Executor)] -> [RDD 1]
[Partition 2] -> [Worker 2 (Executor)] -> [RDD 2]
[Partition 3] -> [Worker 3 (Executor)] -> [RDD 3]
```

---

## 4. Khởi tạo RDD (Creating RDD)

Có hai cách chính để tạo một RDD trong Spark.

### Cách 1: Song song hóa một Collection (Parallelize)
Dùng khi dữ liệu đã có sẵn trong bộ nhớ của Driver (ví dụ: List, Array).

*   **Lưu ý**: Phương thức này yêu cầu toàn bộ dữ liệu phải fit vào RAM của Driver. Thường dùng cho **thử nghiệm (testing)** hoặc xử lý dữ liệu nhỏ.

### Cách 2: Đọc từ nguồn bên ngoài (External Sources)
Dùng khi dữ liệu lớn lưu trữ trên các hệ thống file phân tán (HDFS, S3, HBase, Cassandra...). Dữ liệu sẽ được load động khi cần tính toán.

---

## 5. Code Mẫu và Hướng dẫn Sử dụng

Dưới đây là các ví dụ thực tế để tạo RDD bằng phương thức `parallelize`.

### Ví dụ 1: Python (PySpark)

```python
from pyspark.sql import SparkContext

# Khởi tạo SparkContext
sc = SparkContext("local", "RDD Example")

# Dữ liệu đầu vào là một list trong Python
data = ["fish", "cats", "dogs"]

# Tạo RDD từ list
wordsRDD = sc.parallelize(data)

# Kiểm tra kết quả (Action)
print(wordsRDD.collect()) 
# Output: ['fish', 'cats', 'dogs']

# Dừng SparkContext
sc.stop()
```

### Ví dụ 2: Scala

```scala
import org.apache.spark.{SparkContext, SparkConf}

// Khởi tạo SparkContext
val conf = new SparkConf().setAppName("RDD Example").setMaster("local")
val sc = new SparkContext(conf)

// Tạo RDD từ List Scala
val wordsRDD = sc.parallelize(List("fish", "cats", "dogs"))

// In kết quả
wordsRDD.foreach(println)

// Dừng SparkContext
sc.stop()
```

### Ví dụ 3: Java

```java
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.SparkConf;
import java.util.Arrays;

public class SparkRDDExample {
    public static void main(String[] args) {
        // Khởi tạo SparkConf và JavaSparkContext
        SparkConf conf = new SparkConf().setAppName("RDD Example").setMaster("local");
        JavaSparkContext sc = new JavaSparkContext(conf);

        // Tạo RDD từ List Java
        JavaRDD<String> wordsRDD = sc.parallelize(Arrays.asList("fish", "cats", "dogs"));

        // In kết quả
        wordsRDD.foreach(System.out::println);

        // Dừng SparkContext
        sc.stop();
    }
}
```

---

## 6. Phân tích Sử dụng (Use Case Analysis)

### Khi nào sử dụng RDD?
*   **Xử lý dữ liệu thô (Low-level processing)**: Khi bạn cần kiểm soát hoàn toàn việc xử lý dữ liệu, không cần các tính năng của DataFrame/DataSet (tối ưu hóa tự động).
*   **Bảo tồn dữ liệu không có cấu trúc**: Dữ liệu dạng text, log, hoặc đối tượng tùy chỉnh.
*   **Tính toán phức tạp**: Các thuật toán yêu cầu Lineage graph rõ ràng để xử lý lỗi.

### Sử dụng như thế nào?
1.  **Tạo RDD**: Dùng `sc.parallelize()` (từ collection) hoặc `sc.textFile()` (từ file).
2.  **Biến đổi (Transformations)**: Áp dụng các hàm như `map`, `filter`, `flatMap`, `reduceByKey` để tạo ra RDD mới (lazy evaluation - tính toán lười).
3.  **Hành động (Actions)**: Kích hoạt quá trình tính toán thực sự bằng các lệnh như `collect()`, `count()`, `saveAsTextFile()`.

### Ưu & Nhược điểm

| Tiêu chí | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- |
| **Tốc độ** | Nhanh hơn MapReduce nhờ xử lý trong bộ nhớ (In-memory computing). | Chậm hơn DataFrame/DataSet do không có Catalyst Optimizer. |
| **Tolerant** | Chịu lỗi tốt (Fault tolerance) qua cơ chế Lineage. | Việc tái tạo (recompute) có thể tốn thời gian nếu dữ liệu lớn. |
| **Type Safety** | Kiểm tra lỗi ở thời điểm chạy (Runtime), không kiểm tra trước (Compile time). | Dễ gây lỗi cú pháp nếu không cẩn thận (ví dụ: ép kiểu sai trong Java/Scala). |
| **API** | Linh hoạt, hỗ trợ nhiều ngôn ngữ (Python, Scala, Java, R). | Cú pháp phức tạp hơn so với SQL hoặc DataFrame. |

### Ví dụ thực tế trong ngành công nghiệp
*   **Log Analysis**: Một công ty Fintech sử dụng RDD để đọc hàng triệu dòng log giao dịch mỗi ngày từ HDFS, lọc các giao dịch lỗi (`filter`), và ánh xạ để trích xuất thông tin người dùng (`map`).
*   **Recommender Systems**: Xử lý dữ liệu thô về hành vi người dùng (dạng text) để tạo ma trận tương quan người dùng-sản phẩm trước khi đưa vào các mô hình Machine Learning phức tạp (MLlib).

---

*Tài liệu tham khảo: "7_apache_spark.pdf" - Slide về Apache Spark.*

---

Chào bạn, tôi là một chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết về nội dung slide "7_apache_spark.pdf" của bạn, được trình bày một cách chuyên nghiệp theo yêu cầu.

---

# Apache Spark: RDD, Transformation và Action

Tài liệu này giới thiệu những khái niệm nền tảng của Apache Spark, tập trung vào **RDD (Resilient Distributed Dataset)**, cách thức khởi tạo, và mô hình xử lý dữ liệu dựa trên các thao tác **Transformation** và **Action**.

## 1. Khởi tạo RDD (RDD Initialization)

RDD là cấu trúc dữ liệu cơ bản nhất trong Spark, đại diện cho một tập hợp dữ liệu phân tán và không thay đổi (immutable). RDD có thể được tạo từ các tệp tin văn bản lưu trữ trên nhiều nguồn dữ liệu khác nhau.

### Giải thích Khái niệm
*   **RDD (Resilient Distributed Dataset):** Một bộ sưu tập các đối tượng phân vùng, có khả năng chịu lỗi (fault-tolerant) và được xử lý song song.
*   **SparkContext (sc):** Điểm truy cập chính vào các chức năng của Spark. Khi bạn khởi chạy một ứng dụng Spark, bạn sẽ tạo ra một đối tượng `SparkContext`.
*   **Các nguồn dữ liệu (Sources):** Spark có thể đọc dữ liệu từ nhiều nơi:
    *   **Local File System:** Tệp trên máy tính cục bộ.
    *   **HDFS (Hadoop Distributed File System):** Hệ thống tệp phân tán phổ biến.
    *   **S3 (Amazon Simple Storage Service):** Dịch vụ lưu trữ đám mây của AWS.
    *   **Cassandra/HBase:** Cơ sở dữ liệu NoSQL.

### Code Mẫu (Theo các ngôn ngữ trong slide)

Dưới đây là cách đọc một tệp văn bản từ hệ thống tệp cục bộ (hoặc bất kỳ URI nào được hỗ trợ) bằng Scala, Python, và Java.

#### Scala
```scala
// Khởi tạo SparkContext (thường được cung cấp sẵn trong Spark Shell)
// val sc: SparkContext = ...

// Đọc tệp README.md từ đường dẫn tuyệt đối
// sc.textFile(path, minPartitions) -> path là đường dẫn, minPartitions là số lượng phân vùng tối thiểu (tùy chọn)
val linesRDD = sc.textFile("/path/to/README.md")

// In ra 5 dòng đầu tiên để kiểm tra
linesRDD.take(5).foreach(println)
```

#### Python (PySpark)
```python
# Khởi tạo SparkContext (thường là spark trong PySpark Shell)
# from pyspark import SparkContext
# sc = SparkContext.getOrCreate()

# Đọc tệp README.md
linesRDD = sc.textFile("/path/to/README.md")

# In ra 5 dòng đầu tiên
print(linesRDD.take(5))
```

#### Java
```java
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;

// Giả định bạn đã có JavaSparkContext tên là 'sc'
// JavaSparkContext sc = new JavaSparkContext(...);

JavaRDD<String> lines = sc.textFile("/path/to/README.md");

// In ra 5 dòng đầu tiên
lines.take(5).forEach(System.out::println);
```

### Hướng dẫn Sử dụng
*   **Khi nào sử dụng?**
    *   Khi bạn cần xử lý dữ liệu thô từ các tệp log, CSV, JSON, hoặc bất kỳ định dạng văn bản nào.
    *   Khi dữ liệu nằm rải rác trên các node trong cluster.
*   **Sử dụng như thế nào?**
    *   Sử dụng phương thức `sc.textFile("URI")`. Nếu tệp nằm trên Local, URI phải giống nhau trên tất cả các node. Nếu trên HDFS/S3, dùng URI chuẩn (`hdfs://...`, `s3a://...`).
*   **Ưu & Nhược điểm:**
    *   *Ưu:* Linh hoạt, hỗ trợ nhiều nguồn, tự động phân vùng (partition) dữ liệu để xử lý song song.
    *   *Nhược:* Nếu đọc từ Local File System mà không có HDFS, Spark sẽ sao chép dữ liệu lên các worker node, dẫn đến hiệu quả thấp trong môi trường production.

### Ví dụ Thực tế
Một công ty E-commerce muốn phân tích các tệp log server (Apache/Nginx) để tìm lỗi 404. Họ sử dụng `sc.textFile("hdfs://logs/access.log")` để load dữ liệu hàng terabyte từ HDFS vào Spark.

---

## 2. Mô hình Xử lý: Transformations và Actions

Spark tuân theo mô hình xử lý "Lazy Evaluation" (Tính toán trễ). Các thao tác được chia làm hai loại chính: **Transformations** và **Actions**.

### Giải thích Khái niệm
*   **Transformations (Biến đổi):**
    *   Là các thao tác tạo ra một RDD mới từ RDD hiện có (ví dụ: `filter`, `map`, `flatMap`).
    *   **Lazy (Lười):** Spark không thực thi ngay lập tức khi bạn gọi lệnh. Thay vào đó, nó ghi lại các thao tác vào một **DAG (Directed Acyclic Graph)** - đồ thị thực thi không chu trình.
    *   Việc này cho phép Spark tối ưu hóa toàn bộ luồng xử lý (ví dụ: gộp các bước lọc lại với nhau).
*   **Actions (Hành động):**
    *   Là các thao tác trả về kết quả cho Driver program hoặc lưu dữ liệu ra đĩa.
    *   Kích hoạt quá trình tính toán thực sự của DAG.
    *   Ví dụ: `collect()`, `count()`, `saveAsTextFile()`, `first()`.

### Ví dụ về Transformation (Lọc dữ liệu)

Trong slide, hình ảnh minh họa một RDD ban đầu (`baseRDD`) chứa các log hỗn hợp (Error, Info, Warn). Bằng cách sử dụng transformation `.filter()`, ta tạo ra một RDD mới chỉ chứa các bản ghi lỗi (`errorsRDD`).

**Logic xử lý:**
1.  **Input:** `logLinesRDD` (hỗn hợp).
2.  **Transformation:** `.filter(λ)` (Lọc theo điều kiện).
3.  **Output:** `errorsRDD` (Chỉ chứa "Error").

#### Code Mẫu (Lọc lỗi từ Log)
Giả sử dữ liệu đầu vào có định dạng: `Level, Timestamp, Message`.

```python
# Dữ liệu mẫu (tưởng tượng trong RDD)
# ["Error, 12:00, Connection failed", "Info, 12:01, User login", "Error, 12:02, Timeout"]

# Sử dụng Transformation filter
# Hàm lambda kiểm tra xem dòng có bắt đầu bằng từ "Error" hay không
errorsRDD = logLinesRDD.filter(lambda line: line.startswith("Error"))

# Lệnh này chưa chạy ngay, chỉ tạo ra một RDD mới (lazy)
# errorsRDD chỉ được tính toán khi có Action gọi
```

### Ví dụ về Action

Hình ảnh minh họa `errorsRDD` được chuyển đổi thông qua `.coalesce(2)` (gộp 2 phân vùng) thành `cleanedRDD`. Sau đó, `.collect()` được gọi, và dữ liệu được trả về Driver.

**Logic xử lý:**
1.  **Input:** `errorsRDD`.
2.  **Transformation:** `.coalesce(2)` (Tối ưu hóa phân vùng, giảm số lượng partition).
3.  **Action:** `.collect()` (Thu thập toàn bộ dữ liệu từ các worker node về Driver).

#### Code Mẫu (Thu thập dữ liệu)

```python
# Tiếp theo ví dụ trên, giả sử errorsRDD đã được định nghĩa

# Transformation: Coalesce giảm số lượng partition để tối ưu khi dữ liệu đã nhỏ
cleanedRDD = errorsRDD.coalesce(2)

# Action: Collect
# Lệnh này kích hoạt toàn bộ DAG (filter -> coalesce)
# Dữ liệu được trả về về máy chủ chạy Driver (Driver Node) dưới dạng List/Array
# CẢNH BÁO: Chỉ dùng collect khi dữ liệu nhỏ, tránh tràn bộ nhớ Driver
results = cleanedRDD.collect()

for item in results:
    print(item)
```

### Hướng dẫn Sử dụng
*   **Khi nào sử dụng?**
    *   **Transformations:** Dùng mọi lúc để làm sạch, chuẩn hóa, và chuyển đổi dữ liệu (`map`, `filter`, `join`, `groupBy`).
    *   **Actions:** Dùng khi bạn cần xem kết quả (`collect`), đếm số lượng (`count`), hoặc lưu kết quả (`saveAsTextFile`).
*   **Sử dụng như thế nào?**
    *   Luôn nhớ quy tắc: **Transformation -> Transformation -> ... -> Action**. Bạn có thể xếp chồng hàng trăm transformations, nhưng chỉ khi gọi action thì Spark mới chia sẻ dữ liệu và tính toán.
*   **Ưu & Nhược điểm:**
    *   *Ưu (Lazy Evaluation):* Giúp Spark tối ưu hóa kế hoạch thực thi (Query Optimization), giảm thiểu I/O không cần thiết.
    *   *Nhược:* Khó debug hơn nếu code sai logic, vì lỗi chỉ phát sinh khi gọi Action.

### Ví dụ Thực tế
Trong hệ thống Recommendation Engine:
1.  **Transformation 1:** Đọc dữ liệu hành vi người dùng (`sc.textFile(...)`).
2.  **Transformation 2:** Lọc các hành vi click không hợp lệ (`.filter(...)`).
3.  **Transformation 3:** Tính toán ma trận tương đồng (`.map(...)` và `.reduceByKey(...)`).
4.  **Action:** Lưu kết quả ma trận vào cơ sở dữ liệu (`.saveAsTextFile(...)` hoặc JDBC).

---

## Tóm tắt Phân tích

| Khái niệm | Mô tả | Ví dụ trong Slide |
| :--- | :--- | :--- |
| **RDD** | Tập dữ liệu phân tán, không thay đổi. | `linesRDD`, `logLinesRDD` |
| **SparkContext (sc)** | Cổng giao tiếp chính với Spark Cluster. | `sc.textFile(...)` |
| **Transformation** | Thao tác tạo RDD mới, thực thi chậm (Lazy). | `.filter()`, `.coalesce()` |
| **Action** | Thao tác trả kết quả, kích hoạt tính toán. | `.collect()` |
| **DAG** | Đồ thị thực thi được Spark tạo ra từ các Transformations. | "Execute DAG!" trong slide |

Hy vọng phân tích chi tiết này giúp bạn hiểu rõ hơn về cách Apache Spark vận hành và cách viết code hiệu quả!

---

Chào bạn, với vai trò là một chuyên gia về Big Data và Hệ thống Phân tán, tôi sẽ phân tích chi tiết nội dung từ slide "7_apache_spark.pdf" và trình bày lại một cách chuyên nghiệp, dễ hiểu theo đúng các yêu cầu bạn đưa ra.

Nội dung slide này tập trung vào cách Apache Spark tối ưu hóa kế hoạch thực thi (Execution Plan) và vai trò của các thao tác `cache` và `coalesce` trong việc giảm thiểu chi phí tính toán.

---

# Phân tích Kế hoạch Thực thi và Tối ưu hóa trong Apache Spark

Slide này min họa sự khác biệt giữa kế hoạch thực thi Logic và Physical trong Spark, đồng thời chỉ ra cách các thao tác biến đổi dữ liệu (Transformations) được tối ưu hóa để tránh lặp lại các công việc tính toán tốn kém.

## 1. Kế hoạch Thực thi: Logical Plan vs. Physical Plan

Trong Spark, một tác vụ được xử lý qua hai giai đoạn lập kế hoạch chính.

### Giải thích Khái niệm

*   **Logical Plan (Kế hoạch Logic):** Đây là biểu diễn trừu tượng của các thao tác dữ liệu mà người dùng định nghĩa. Nó mô tả "cái gì" cần được thực hiện (ví dụ: lọc dữ liệu, gom nhóm) nhưng không quan tâm "làm thế nào" để thực hiện nó một cách hiệu quả. Các thao tác này được biểu diễn dưới dạng một Directed Acyclic Graph (DAG) của các RDDs.
*   **Physical Plan (Kế hoạch Vật lý):** Đây là kế hoạch thực thi cuối cùng mà Spark tạo ra sau khi tối ưu hóa. Nó mô tả "cách thức" thực hiện các thao tác, bao gồm việc chia dữ liệu thành các phân vùng (partitions), tối ưu hóa các thao tác theo chuỗi (pipelining), và quyết định xem có nên thực thi lại các bước trước đó hay không.

### Phân tích từ Slide

*   **Logical View (Hình ảnh trên cùng):**
    *   `logLinesRDD` -> `.filter(λ)` -> `errorsRDD` -> `.coalesce(2)` -> `cleanedRDD` -> `.collect()` hoặc `.saveAsTextFile()`.
    *   Đây là cách người dùng viết code, thể hiện luồng xử lý tuần tự.

*   **Physical View (Hình ảnh dưới cùng):**
    *   Spark không thực thi y nguyên các bước như trên. Thay vào đó, nó tối ưu hóa.
    *   **Pipelining (Nối ống):** Các thao tác `filter` có thể được thực thi trên cùng một task mà không cần phải ghi dữ liệu trung gian ra đĩa hoặc shuffle dữ liệu.
    *   **Lazy Evaluation (Thực thi trì hoãn):** Các thao tác transformation chỉ được thực thi khi có action (như `collect()`, `saveAsTextFile()`, `count()`).

### Ví dụ Code Mẫu

Dưới đây là đoạn code tương ứng với các thao tác trong slide.

```python
from pyspark.sql import SparkSession
from pyspark import SparkContext

# Khởi tạo Spark Context
sc = SparkContext.getOrCreate()

# 1. Tạo RDD từ file log (Logical Plan bắt đầu)
# Giả sử chúng ta có một file log
logLinesRDD = sc.textFile("hdfs://path/to/logfile.log")

# 2. Lọc các dòng lỗi (Transformation)
# Lambda function để kiểm tra xem dòng có chứa từ "Error" không
error_filter_lambda = lambda line: "Error" in line
errorsRDD = logLinesRDD.filter(error_filter_lambda)

# 3. Coalesce: Giảm số lượng partition về 2 (Transformation)
# Thường dùng để giảm số file output hoặc optimize sau khi filter
cleanedRDD = errorsRDD.coalesce(2)

# 4. Action: Collect (Thực thi Physical Plan)
# Khiến Spark thực thi toàn bộ DAG
collected_data = cleanedRDD.collect()
for item in collected_data:
    print(item)

# Hoặc Action: Save
# cleanedRDD.saveAsTextFile("hdfs://path/to/output_errors")
```

---

## 2. Tối ưu hóa với `cache()` và Chi phí tính toán

Slide so sánh hai kịch bản:
1.  **Không sử dụng cache:** Phải đọc và xử lý dữ liệu lại từ đầu mỗi khi có action mới.
2.  **Sử dụng cache:** Lưu dữ liệu đã xử lý vào bộ nhớ, giúp các action sau nhanh hơn.

### Giải thích Khái niệm

*   **RDD (Resilient Distributed Dataset):** Là cấu trúc dữ liệu cơ bản của Spark, phân tán trên các node trong cluster.
*   **Transformation:** Là các thao tác tạo ra một RDD mới từ RDD cũ (ví dụ: `filter`, `map`, `coalesce`). Chúng là **lazy** (trì hoãn).
*   **Action:** Là các thao tác trả về kết quả về Driver hoặc lưu vào storage (ví dụ: `collect`, `count`, `saveAsTextFile`). Chúng kích hoạt việc thực thi các transformation.
*   **`cache()` / `persist()`:** Các thao tác này đánh dấu RDD cần được lưu vào bộ nhớ (memory) hoặc đĩa (disk) sau khi được tính toán lần đầu tiên.
*   **`coalesce(n)`:** Giảm số lượng partition của RDD xuống `n` partition. Thao tác này thường được sử dụng để giảm độ song song (parallelism) sau khi lọc dữ liệu, giúp tránh việc tạo ra quá nhiều file output nhỏ (small files problem) khi ghi ra đĩa.

### Phân tích từ Slide

*   **Scenario 1 (Không có cache):**
    *   Khi gọi `collect()` trên `cleanedRDD`, Spark phải thực thi chuỗi: `read logLinesRDD` -> `filter` -> `coalesce`.
    *   Nếu sau đó gọi một action khác (ví dụ: đếm `errorMsg1RDD`), Spark lại phải thực thi lại toàn bộ chuỗi từ đầu. Điều này rất tốn kém nếu dữ liệu lớn.

*   **Scenario 2 (Có `cache()`):**
    *   Action đầu tiên (`collect()` hoặc `saveAsTextFile()`) thực thi chuỗi xử lý và lưu kết quả của `errorsRDD` (hoặc `cleanedRDD`) vào bộ nhớ.
    *   Action thứ hai (`count()` trên `errorMsg1RDD`) có thể lấy dữ liệu trực tiếp từ bộ nhớ đã được cache, bỏ qua bước đọc file log và filter ban đầu.

### Ví dụ Code Mẫu minh họa sự khác biệt

```python
# --- KỊCH BẢN 1: KHÔNG SỬ DỤNG CACHE (TỐN KÉM) ---
print("Kịch bản 1: Không dùng cache")

# Action 1: Lưu các lỗi ra file
# Spark thực thi: Read -> Filter -> Coalesce -> Write
errorsRDD.coalesce(2).saveAsTextFile("hdfs://output/errors_v1")

# Action 2: Đếm số lượng lỗi
# Spark PHẢI LÀM LẠI TỪ ĐẦU: Read -> Filter -> Coalesce -> Count
# Rất lãng phí tài nguyên!
error_count = errorsRDD.count()
print(f"Tổng số lỗi: {error_count}")


# --- KỊCH BẢN 2: SỬ DỤNG CACHE (HIỆU QUẢ) ---
print("\nKịch bản 2: Có dùng cache")

# Bước 1: Cache RDD đã được filter
# Lưu ý: Cache không phải là action, nó chỉ đánh dấu.
errorsRDD.cache() 

# Action 1: Lưu các lỗi ra file
# Spark thực thi: Read -> Filter -> Coalesce -> Write
# Đồng thời, do có cache, kết quả của errorsRDD (sau filter) được lưu vào memory
errorsRDD.coalesce(2).saveAsTextFile("hdfs://output/errors_v2")

# Action 2: Đếm số lượng lỗi
# Spark chỉ cần đọc từ memory (cache) -> Count
# Rất nhanh!
error_count = errorsRDD.count()
print(f"Tổng số lỗi: {error_count}")
```

---

## 3. Phân tích Execution Plan: Partition >> Task >> Partition

Slide cuối cùng min họa mối quan hệ giữa **Partition**, **Task**, và **RDD**.

### Giải thích Khái niệm

*   **Partition:** Một phần nhỏ của dữ liệu RDD, được lưu trữ trên một Executor (Node). Dữ liệu lớn được chia thành nhiều partition để xử lý song song.
*   **Task:** Đơn vị công việc nhỏ nhất được Spark gửi đến Executor. Một Task xử lý một Partition của dữ liệu.
*   **Stage:** Một giai đoạn của job, chứa nhiều Task có thể thực thi song song. Stage được chia cắt bởi các thao tác shuffle (như `reduceByKey`, `join`).
*   **HadoopRDD:** RDD gốc thường đọc từ HDFS, được chia theo các block của file (ví dụ: 128MB/block).

### Phân tích từ Slide

*   **Hình ảnh:** `logLinesRDD (HadoopRDD)` được chia thành các partition, và các Task (Task-1, Task-2, Task-3, Task-4) được chạy song song trên các partition này.
*   **Thao tác `filter`:** Thao tác `filter(λ)` được thực thi "trong pipeline" trên từng Task. Nghĩa là Task-1 đọc một partition của `logLinesRDD`, áp dụng filter, và tạo ra một phần của `errorsRDD` (filteredRDD) mà không cần chờ các Task khác.
*   **Kết quả:** Mỗi Task tạo ra một phần của RDD mới trên Executor của nó.

### Ví dụ thực tế trong ngành

Giả sử bạn có 1 TB dữ liệu log từ server (tương đương 8,000 block 128MB trên HDFS).

1.  **Input:** Spark tạo ra `logLinesRDD` với 8,000 partitions.
2.  **Execution:** Spark khởi động 8,000 Task (hoặc ít hơn tùy cấu hình cluster).
3.  **Filter:** Mỗi Task xử lý 1 partition, lọc ra các dòng "Error". Giả sử sau khi lọc, mỗi partition chỉ còn lại 1MB dữ liệu.
4.  **Coalesce:** Nếu bạn gọi `.coalesce(10)`, Spark sẽ gom 8,000 partition nhỏ này lại chỉ còn 10 partition lớn hơn để chuẩn bị ghi ra file hoặc tính toán tiếp. Điều này giúp tránh việc tạo ra 8,000 file output nhỏ xíu, gây hiệu ứng "Small Files Problem" làm chậm hệ sinh thái HDFS/Cloud Storage.

---

## 4. Tóm tắt: Ưu & Nhược điểm và Hướng dẫn sử dụng

| Khái niệm | Khi nào sử dụng? (Use Cases) | Sử dụng như thế nào? (How to use) | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- | :--- | :--- |
| **`cache()` / `persist()`** | Khi bạn cần truy cập同一個 RDD nhiều lần qua các Action khác nhau (ví dụ: train model xong rồi predict, hoặc visualize dữ liệu). | Gọi `.cache()` hoặc `.persist()` trên RDD ngay sau khi tạo nó (trước Action đầu tiên). | Tăng tốc độ xử lý đáng kể bằng cách tránh tính toán lại. | Tiêu tốn bộ nhớ RAM của Executor. Nếu dữ liệu quá lớn, có thể gây OOM (Out of Memory). |
| **`coalesce(n)`** | Khi số lượng partition quá lớn sau khi filter, và bạn muốn giảm độ song song để tối ưu ghi file (giảm small files) hoặc giảm overhead task. | Gọi `.coalesce(n)` trước khi ghi file (`saveAsTextFile`) hoặc trước các action tổng hợp. | Giảm số file output, tăng hiệu suất ghi file. | Có thể gây mất cân bằng dữ liệu (một partition chứa nhiều dữ liệu hơn các partition khác). |
| **Lazy Evaluation** | Luôn luôn. Đây là bản chất của Spark. | Viết chuỗi các Transformation, sau đó mới gọi Action. | Cho phép Spark tối ưu hóa toàn bộ DAG trước khi thực thi (ví dụ: gộp nhiều filter lại). | Khó debug hơn nếu không quen với mô hình này (lỗi thường chỉ hiện khi gọi Action). |

## Kết luận

Slide "7_apache_spark.pdf" cung cấp một cái nhìn sâu sắc về cách Spark tối ưu hóa việc xử lý dữ liệu lớn. Bài học chính là: **Hiểu được sự khác biệt giữa Logical và Physical Plan, và biết cách sử dụng `cache()` cùng `coalesce()` một cách thông minh sẽ giúp bạn xây dựng các hệ thống Big Data hiệu quả và tiết kiệm chi phí.**

---

Chào bạn, với vai trò là một chuyên gia về Big Data và Hệ thống Phân tán, tôi sẽ phân tích và trình bày lại nội dung từ slide "7_apache_spark.pdf" một cách chi tiết, chuyên nghiệp và dễ hiểu theo đúng các yêu cầu bạn đã đưa ra.

***

# Apache Spark: Lập trình Phân tán & Kiến trúc RDD

Tài liệu này t tổng hợp các khái niệm cốt lõi về cách lập trình và xử lý lỗi trong Apache Spark, tập trung vào mô hình RDD (Resilient Distributed Dataset).

## 1. Khái niệm Nền tảng: RDD và Lineage

**RDD (Resilient Distributed Dataset)** là cấu trúc dữ liệu cơ bản của Spark. Nó là một tập hợp các đối tượng phân tán có thể chịu lỗi (fault-tolerant).

### Giải thích khái niệm

*   **Resilient (Chịu lỗi):** Khả năng tự động khôi phục khi một node trong cluster bị lỗi.
*   **Distributed (Phân tán):** Dữ liệu được chia nhỏ và lưu trữ trên nhiều node khác nhau trong cluster.
*   **Dataset (Tập dữ liệu):** Một tập hợp các phần tử dữ liệu.

Cơ chế chính giúp RDD chịu lỗi là **Lineage (Dòng dõi)**. Thay vì lưu trữ dữ liệu sao lưu (replication) thường tốn kém, RDD lưu trữ **lịch sử các thao tác (transformations)** đã áp dụng lên dữ liệu gốc. Khi một phần dữ liệu bị mất, Spark sẽ dùng Lineage để tính toán lại phần dữ liệu đó từ dữ liệu gốc.

### Hướng dẫn sử dụng

*   **Khi nào sử dụng?**
    *   Khi cần xử lý dữ liệu lớn với yêu cầu về độ tin cậy cao.
    *   Khi dữ liệu có cấu trúc không rõ ràng hoặc bán cấu trúc.
    *   Cần truy cập ở mức độ thấp (low-level access) để tối ưu hóa thủ công.
*   **Sử dụng như thế nào?**
    1.  Tạo RDD từ nguồn (disk, memory).
    2.  Áp dụng các phép biến đổi (Transformations) để định nghĩa luồng xử lý.
    3.  Spark sẽ xây dựng một đồ thị Directed Acyclic Graph (DAG) của các phép toán.
    4.  Khi Action được gọi, Spark mới tính toán và sử dụng Lineage để tự động tái tạo dữ liệu nếu cần.
*   **Ưu & Nhược điểm:**
    *   **Ưu:** Khả năng chịu lỗi cao, chi phí lưu trữ thấp (không cần replication), linh hoạt trong xử lý.
    *   **Nhược:** Nếu đồ thị quá dài (quá nhiều bước transformation), việc tái tạo (recompute) một phần dữ liệu bị mất có thể chậm.

### Ví dụ thực tế

Trong hệ thống ETL (Extract, Transform, Load) hàng ngày, một job Spark có thể đọc 1TB log từ HDFS, lọc lỗi, rồi join với bảng user. Nếu một node bị chết giữa chừng khi đang thực hiện phép `join`, Spark không cần đọc lại toàn bộ 1TB log, mà chỉ cần đọc lại phần dữ liệu gốc tương ứng và thực hiện lại các bước `filter` và `join` trên node khác.

---

## 2. Quy trình Lập trình trên Spark (Programming Model)

Quy trình này tuân theo mô hình **Lazy Evaluation** (Tính toán trễ).

### Các bước thực hiện

1.  **Tạo RDD (Create RDD):** Khởi tạo dữ liệu từ nguồn (HDFS, S3, local file) hoặc từ collections trong bộ nhớ (List, Array).
2.  **Biến đổi (Transformations):** Áp dụng các hàm như `map`, `filter` để tạo ra các RDD mới. Các bước này **không thực thi ngay lập tức** mà chỉ xây dựng đồ thị (Lineage).
3.  **Cache (Lưu vào bộ nhớ):** Nếu RDD trung gian được sử dụng lại nhiều lần, gọi `cache()` hoặc `persist()` để lưu vào RAM, tránh tính toán lại.
4.  **Hành động (Actions):** Kích hoạt quá trình tính toán thực sự và trả kết quả về Driver hoặc lưu ra file.

### Ví dụ minh họa quy trình (Python)

```python
from pyspark import SparkContext, SparkConf

# Cấu hình và khởi tạo Context
conf = SparkConf().setAppName("WordCountExample").setMaster("local[*]")
sc = SparkContext(conf=conf)

# 1. Tạo RDD từ file text (Lazy)
# Dữ liệu chưa được đọc ngay lập tức
lines_rdd = sc.textFile("hdfs://path/to/log.txt")

# 2. Transformations (Lazy)
# Biến đổi thành các từ (flatMap), rồi đếm (reduceByKey)
# Lúc này, Spark chỉ ghi nhận DAG, chưa chạy
words_rdd = lines_rdd.flatMap(lambda line: line.split(" "))
filtered_words = words_rdd.filter(lambda word: word != "")
word_counts = filtered_words.map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)

# 3. Cache (Tùy chọn)
# Nếu cần dùng lại word_counts nhiều lần
word_counts.cache()

# 4. Actions (Trigger Execution)
# Gọi action thì Spark mới chạy job và in kết quả
print(word_counts.collect()) 
# Hoặc lưu kết quả
# word_counts.saveAsTextFile("hdfs://path/to/output")
```

---

## 3. Phép biến đổi - Transformations (Lazy)

Đây là các thao tác tạo ra RDD mới từ RDD cũ. Chúng được thực thi **trễ (Lazy)**.

### Danh sách và giải thích một số Transformations quan trọng

| Phép biến đổi (Transformation) | Mô tả (Description) | Use Case (Khi nào dùng?) |
| :--- | :--- | :--- |
| **`map(func)`** | Áp dụng hàm `func` lên từng phần tử và trả về một RDD mới. | Chuyển đổi định dạng dữ liệu (ví dụ: từ JSON string sang Object). |
| **`filter(func)`** | Lọc các phần tử mà hàm `func` trả về `True`. | Loại bỏ dữ liệu rác, chọn các bản ghi thỏa mãn điều kiện. |
| **`flatMap(func)`** | Tương tự `map`, nhưng hàm có thể trả về nhiều phần tử (list) và "phẳng" hóa kết quả. | Tách một dòng văn bản thành nhiều từ (Word Count). |
| **`groupByKey()`** | Nhóm các cặp (Key, Value) theo Key. | Khi cần tập hợp tất cả các giá trị của một Key lại với nhau. |
| **`reduceByKey(func)`** | Nhóm theo Key và kết hợp các giá trị bằng hàm `func` (tại các worker trước khi gửi dữ liệu). | **Tối ưu hơn `groupByKey`**. Dùng để tính tổng, tìm max/min theo nhóm. |
| **`union()`** | Hợp nhất hai RDD. | Kết hợp dữ liệu từ nhiều nguồn hoặc nhiều thời điểm. |
| **`distinct()`** | Loại bỏ các phần tử trùng lặp. | Chuẩn hóa dữ liệu, loại bỏ bản ghi duplicate. |
| **`join()`** | Nối hai RDD dựa trên Key chung. | Kết hợp thông tin từ hai nguồn (ví dụ: Log và User Info). |
| **`sortByKey()`** | Sắp xếp RDD (Key, Value) theo Key. | Báo cáo cần dữ liệu được sắp xếp. |

### Ví dụ Code Minh họa Transformations

```python
# Giả sử có RDD đầu vào: (id, score)
data = sc.parallelize([(1, 80), (2, 90), (1, 85), (3, 70)])

# 1. Filter: Lọc điểm >= 80
high_scores = data.filter(lambda x: x[1] >= 80) 
# Kết quả: [(1, 80), (2, 90), (1, 85)]

# 2. GroupByKey: Nhóm theo ID
# Kết quả sẽ là: (1, [80, 85]), (2, [90])
grouped = data.groupByKey()
# grouped.mapValues(list).collect() -> [(1, [80, 85]), (2, [90]), (3, [70])]

# 3. ReduceByKey: Tính điểm trung bình theo ID
# Tốt hơn GroupByKey vì giảm lượng dữ liệu truyền mạng
avg_scores = data.mapValues(lambda x: (x, 1)) \
                 .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])) \
                 .mapValues(lambda x: x[0] / x[1])
# avg_scores.collect() -> [(1, 82.5), (2, 90.0), (3, 70.0)]
```

---

## 4. Phép hành động - Actions

Actions là các thao tác **kích hoạt việc thực thi** toàn bộ đồ thị tính toán (DAG) và trả kết quả về Driver hoặc lưu xuống storage.

### Danh sách và giải thích một số Actions quan trọng

| Hành động (Action) | Mô tả (Description) | Use Case (Khi nào dùng?) |
| :--- | :--- | :--- |
| **`reduce(func)`** | Giảm các phần tử của RDD thành một giá trị duy nhất bằng hàm kết hợp. | Tính tổng, nhân, tìm max/min của toàn bộ dữ liệu. |
| **`collect()`** | Trả về toàn bộ các phần tử của RDD về Driver dưới dạng List. | **Chỉ dùng cho dữ liệu nhỏ** (debugging, unit test). |
| **`count()`** | Đếm số lượng phần tử trong RDD. | Thống kê tổng số bản ghi. |
| **`take(n)`** | Lấy `n` phần tử đầu tiên về Driver. | Xem trước dữ liệu (preview). |
| **`first()`** | Lấy phần tử đầu tiên. | Kiểm tra dữ liệu đầu vào. |
| **`foreach(func)`** | Áp dụng hàm lên từng phần tử (không trả về kết quả về Driver). | Gửi dữ liệu vào database, in log. |
| **`saveAsTextFile(path)`** | Lưu RDD thành file text (thường là nhiều part file). | Xuất kết quả ETL ra HDFS/S3. |
| **`countByKey()`** | Đếm số lượng phần tử theo từng Key và trả về Map về Driver. | Thống kê phân phối dữ liệu theo Key. |

### Ví dụ Code Minh họa Actions

```python
# Tiếp tục ví dụ RDD: (id, score)
data = sc.parallelize([(1, 80), (2, 90), (1, 85), (3, 70)])

# 1. count()
total_records = data.count() 
# Kết quả: 4

# 2. reduce()
# Tính tổng điểm tất cả học sinh
total_score = data.map(lambda x: x[1]).reduce(lambda a, b: a + b)
# Kết quả: 80 + 90 + 85 + 70 = 325

# 3. take()
# Lấy 2 bản ghi đầu tiên
top_2 = data.take(2)
# Kết quả: [(1, 80), (2, 90)]

# 4. saveAsTextFile
# Lưu kết quả ra HDFS (không in ra màn hình)
# data.saveAsTextFile("hdfs://output/scores")
```

---

## 5. Tóm tắt và Best Practices

1.  **Tránh `groupByKey`:** Luôn ưu tiên `reduceByKey` hoặc `aggregateByKey`. `groupByKey` sẽ shuffle toàn bộ dữ liệu (gây nặng mạng và bộ nhớ), trong khi `reduceByKey` thực hiện giảm thiểu (combine) dữ liệu tại worker trước khi shuffle.
2.  **Cache dữ liệu trung gian:** Nếu một RDD được dùng lại nhiều lần trong các Actions khác nhau, hãy gọi `RDD.cache()` hoặc `RDD.persist()`. Nếu không, Spark sẽ tính toán lại từ đầu mỗi khi có Action.
3.  **Hiểu về Lineage:** Khi lỗi xảy ra, bạn không cần lo lắng, Spark sẽ tự rebuild. Tuy nhiên, hãy đảm bảo dữ liệu nguồn (source) luôn sẵn sàng.
4.  **Laziness:** Luôn nhớ rằng Transformations chỉ là "kế hoạch". Chỉ khi có Action thì "kế hoạch" đó mới được thực thi. Điều này cho phép Spark tối ưu hóa luồng tính toán (ví dụ: gộp các bước `map` lại với nhau).

Hy vọng tài liệu tổng hợp này giúp bạn hiểu rõ hơn về Apache Spark và cách vận hành nó trong các hệ thống Big Data thực tế

---

Chào bạn, tôi là chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết và trình bày lại nội dung từ tài liệu slide "7_apache_spark.pdf" theo yêu cầu của bạn.

---

# Apache Spark: Các Khái niệm Nâng cao về RDD, DataFrame và Optimizer

Tài liệu này cung cấp cái nhìn tổng quan về các loại RDD đặc thù, cách thiết lập môi trường thực hành, và quan trọng nhất là khái niệm **DataFrame** - lớp trừu tượng dữ liệu chính trong Spark hiện đại, cùng các thao tác biến đổi (Transformations).

## 1. Các Dạng RDD Phổ biến (Common RDD Types)

Trong Apache Spark, **RDD (Resilient Distributed Dataset)** là cấu trúc dữ liệu cơ bản. Tuy nhiên, để tối ưu hóa cho các nguồn dữ liệu và thao tác cụ thể, Spark cung cấp nhiều lớp RDD con (Subclasses).

### Giải thích Khái niệm
Mặc dù **DataFrame** và **Dataset** là API chính (high-level) hiện nay, việc hiểu về các loại RDD giúp ta nắm được底层 (low-level) hoạt động của Spark, đặc biệt khi xử lý các nguồn dữ liệu đặc thù hoặc giao tiếp với các hệ thống khác.

### Phân loại chi tiết

| Dạng RDD | Mô tả & Công dụng |
| :--- | :--- |
| **HadoopRDD** | RDD gốc để tương thích với **Hadoop MapReduce**. Nó đọc dữ liệu từ các InputFormat của Hadoop (ví dụ: TextInputFormat). |
| **JdbcRDD** | Tối ưu để đọc dữ liệu trực tiếp từ các cơ sở dữ liệu quan hệ (RDBMS) qua **JDBC**. Nó thực hiện truy vấn song song dựa trên các vùng (partition) của khóa chính. |
| **JsonRDD** | Dùng để parse dữ liệu JSON. (Lưu ý: Trong Spark hiện đại, `spark.read.json()` thường được dùng thay cho tạo thủ công). |
| **PairRDD** | Loại RDD quan trọng nhất cho các thao tác **Key-Value** (như MapReduce). Nó cho phép thực hiện các phép toán `reduceByKey`, `groupByKey`, `join`. |
| **UnionRDD** | Tạo ra bằng cách hợp nhất (union) nhiều RDD khác nhau thành một RDD duy nhất. |
| **FilteredRDD / MappedRDD** | Kết quả của các phép toán `filter()` và `map()`. Đây là các RDD được tạo ra trong quá trình xử lý (Transformation). |
| **CassandraRDD, GeoRDD, VertexRDD, EdgeRDD** | Các RDD chuyên biệt cho các hệ thống cụ thể: **Cassandra** (CSDL NoSQL), **ESRI** (Bản đồ không gian địa lý), và **GraphX** (Xử lý đồ thị - Vertex/Edge). |

### Code Mẫu: Tạo và Sử dụng PairRDD
Dưới đây là ví dụ về cách tạo PairRDD từ một List và thực hiện phép toán `reduceByKey`.

```python
from pyspark import SparkContext, SparkConf

# Khởi tạo Spark Context
conf = SparkConf().setAppName("PairRDDExample").setMaster("local[*]")
sc = SparkContext(conf=conf)

# Dữ liệu đầu vào: (Key, Value)
data = [("apple", 1), ("banana", 1), ("apple", 2), ("orange", 1)]

# Tạo PairRDD
pair_rdd = sc.parallelize(data)

# Phép toán Transformation: reduceByKey để cộng giá trị theo Key
# Tương đương với Phase Shuffle trong MapReduce
word_counts = pair_rdd.reduceByKey(lambda a, b: a + b)

# Action: Collect để in kết quả
print(word_counts.collect()) 
# Output: [('banana', 1), ('orange', 1), ('apple', 3)]
```

---

## 2. RDD Demo: Thiết lập Môi trường với Docker

Slide đề cập đến việc sử dụng Docker để chạy môi trường **Jupyter Notebook** tích hợp **PySpark**, giúp việc học và thử nghiệm RDD/DataFrame trở nên dễ dàng hơn.

### Hướng dẫn Sử dụng

**Khi nào sử dụng?**
*   Khi bạn cần một môi trường Spark độc lập, cô lập để chạy thử nghiệm, phân tích dữ liệu nhanh (EDA) mà không cần cài đặt phức tạp trên hệ điều hành.
*   Phù hợp cho người mới học hoặc phát triển các prototype.

**Sử dụng như thế nào?**

1.  **Tải Image (Pull):**
    ```bash
    docker pull jupyter/pyspark-notebook
    ```
2.  **Chạy Container (Run):**
    Lệnh này ánh xạ port 8888 của container ra port 8888 của máy chủ để truy cập Jupyter.
    ```bash
    docker run -p 8888:8888 jupyter/pyspark-notebook
    ```
3.  **Truy cập:**
    *   Mở trình duyệt và truy cập: `http://127.0.0.1:8888/tree`
    *   *Lưu ý cho Windows:* Nếu bạn dùng Docker Toolbox (cũ) hoặc Docker trên WSL2 có cấu hình đặc biệt, địa chỉ có thể là `http://192.168.99.100:8888/tree`.
4.  **Làm việc:**
    *   Copy **Token** được in ra trong terminal Docker.
    *   Upload file notebook (`.ipynb`) hoặc tạo mới để viết code PySpark.

---

## 3. DataFrame: Lớp Trừu tượng Chính của Spark

Kể từ Spark 2.0, **DataFrame** (và **Dataset**) là API chính được khuyến khích sử dụng thay vì RDD trực tiếp do hiệu suất và tối ưu hóa tốt hơn.

### Giải thích Khái niệm

*   **Abstraction (Trừu tượng hóa):** DataFrame giống như bảng trong SQL hoặc một bảng trong Pandas, nhưng dữ liệu được phân tán trên nhiều node.
*   **Immutability (Tính bất biến):** Một khi DataFrame được tạo, nó không thể thay đổi. Mọi thao tác biến đổi sẽ tạo ra một DataFrame mới.
*   **Lineage (Dòng dõi):** Spark ghi lại toàn bộ các thao tác (transformation) đã thực hiện lên DataFrame. Nếu một node bị lỗi, Spark có thể dùng Lineage để tái tạo (recompute) dữ liệu bị mất một cách chính xác.
*   **Lazy Evaluation (Thực thi muộn):** Các thao tác biến đổi không được thực thi ngay lập tức mà chỉ được lưu lại. Việc tính toán thực sự chỉ diễn ra khi một **Action** (như `show()`, `count()`, `save()`) được gọi.

### Các cách khởi tạo DataFrame

Slide liệt kê 3 cách chính:
1.  **Từ Collections trong bộ nhớ:** Dùng `createDataFrame` từ List, Tuple.
2.  **Từ DataFrame/Pandas:** Chuyển đổi từ các cấu trúc dữ liệu có sẵn.
3.  **Từ File:** Đọc trực tiếp từ HDFS, S3, Local file (CSV, Parquet, JSON).

### Code Mẫu: Khởi tạo và Thao tác với DataFrame

Dưới đây là ví dụ minh họa đoạn code trong slide và các thao tác Transformation.

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Khởi tạo Spark Session (Cần thiết cho DataFrame API)
spark = SparkSession.builder.appName("DataFrameDemo").getOrCreate()

# --- 1. Khởi tạo từ Collections (Code từ slide) ---
data = [("Alice", 1), ("Bob", 2), ("Bob", 2)]
# Định nghĩa Schema (Tên cột)
columns = ["name", "age"]

# Tạo DataFrame
df1 = spark.createDataFrame(data, columns)

print("Original DataFrame:")
df1.show()

# --- 2. Các Transformations ---

# Transformation 1: select() - Chọn cột
df_select = df1.select("name")

# Transformation 2: filter() / where() - Lọc dòng
# Lọc những người có tuổi > 1
df_filter = df1.filter(df1.age > 1)

# Transformation 3: distinct() - Loại bỏ trùng lặp
# Kết quả: ('Alice', 1), ('Bob', 2) (vì ('Bob', 2) bị loại bỏ 1 bản ghi)
df_distinct = df1.distinct()

# Transformation 4: sort() - Sắp xếp
df_sort = df1.sort(df1.age.desc(), df1.name.asc())

# --- 3. Action ---
# Chỉ khi gọi show() thì Spark mới thực thi các Transformation ở trên
print("DataFrame sau khi distinct và sort:")
df_sort.show()

# Dừng Spark Session
spark.stop()
```

---

## 4. Phân tích Transformations trong DataFrame

Slide cung cấp bảng tóm tắt các phép biến đổi quan trọng. Dưới đây là giải thích chi tiết và Use Cases.

### Bảng Transformations

| Transformation | Mô tả chi tiết | Use Cases (Khi nào dùng?) |
| :--- | :--- | :--- |
| **`select(*cols)`** | Chọn các cột cụ thể để giữ lại, tương đương `SELECT col1, col2` trong SQL. | Khi bạn chỉ cần một tập con dữ liệu để giảm dung lượng bộ nhớ hoặc chuẩn bị dữ liệu cho bước tiếp theo. |
| **`drop(col)`** | Xóa các cột không cần thiết. | Loại bỏ các cột nhạy cảm (PII), cột rác (garbage columns) để làm sạch dữ liệu. |
| **`filter(func)` / `where(func)`** | Lọc các dòng (rows) dựa trên điều kiện logic. | Phân tích dữ liệu theo phân khúc (ví dụ: Lấy giao dịch có giá trị > 100 triệu). |
| **`distinct()`** | Loại bỏ các bản ghi trùng lặp hoàn toàn. | Chuẩn hóa dữ liệu, loại bỏ dữ liệu thừa từ các nguồn đồng bộ. |
| **`sort(*cols)`** | Sắp xếp dữ liệu theo các cột chỉ định (mặc định tăng dần). | Chuẩn bị dữ liệu để xuất báo cáo, hoặc tối ưu hóa cho các thao tác sau này (như `rangePartition`). |

### Ưu & Nhược điểm của DataFrame so với RDD

| Tiêu chí | DataFrame | RDD (Low-level) |
| :--- | :--- | :--- |
| **Optimization (Tối ưu)** | **Cao (Tự động):** Dùng **Catalyst Optimizer** để tối ưu hóa kế hoạch thực thi (Logical & Physical Plan). | **Thấp:** Người dùng phải tự tối ưu hóa code. |
| **Performance (Hiệu năng)** | **Tốt hơn:** Sử dụng **Tungsten Execution Engine** (Quản lý bộ nhớ, tối ưu CPU). | **Thấp hơn:** Không tối ưu hóa bộ nhớ (Java Object overhead). |
| **Ease of Use** | **Dễ:** Cú pháp giống SQL, Pandas. | **Khó:** Cần hiểu sâu về Function Programming (map, reduce, lambda). |
| **Type Safety** | **Runtime Check:** Lỗi chỉ phát hiện khi chạy. | **Compile-time (Scala):** An toàn kiểu biên dịch (chủ yếu ở Scala, Python thì linh hoạt nhưng dễ lỗi logic). |

---

## 5. Ví dụ Thực tế trong Ngành Công Nghiệp

**Bài toán: ETL và Phân tích Dữ liệu Giao dịch Tài chính**

**Scenario:** Một ngân hàng có hệ thống giao dịch xử lý hàng triệu giao dịch mỗi ngày từ các nguồn khác nhau (HDFS, Database).

**Cách tiếp cận sử dụng kiến thức từ slide:**

1.  **Đọc dữ liệu (Input):**
    *   Sử dụng **`spark.read.jdbc`** (tương tự `JdbcRDD`) để đọc dữ liệu lịch sử từ Database Oracle.
    *   Sử dụng **`spark.read.json`** để đọc log giao dịch realtime từ HDFS.

2.  **Xử lý và Tối ưu (Transformations):**
    *   **`filter()`**: Lọc các giao dịch hợp lệ (status = 'SUCCESS') và loại bỏ giao dịch test.
    *   **`select()`**: Chọn các cột quan trọng: `user_id`, `amount`, `timestamp`. Bỏ các cột metadata không dùng.
    *   **`distinct()`**: Loại bỏ các bản ghi giao dịch bị duplicate do lỗi network (giao dịch bị gửi 2 lần).
    *   **`sort()`**: Sắp xếp theo `timestamp` để phân tích hành vi người dùng theo thời gian.

3.  **Lưu trữ (Output):**
    *   Ghi kết quả vào Data Warehouse (như Hive) hoặc file **Parquet** để tối ưu hóa cho việc truy vấn sau này.

**Lợi ích:**
*   **Tốc độ:** Xử lý hàng TB dữ liệu trong vài phút nhờ cơ chế song song hóa và tối ưu của DataFrame.
*   **Tính ổn định:** Nhờ cơ chế **Lineage**, nếu node bị lỗi trong quá trình xử lý, Spark tự động tái tính toán mà không mất dữ liệu.

---

Dưới đây là tài liệu phân tích và tổng hợp chi tiết về Apache Spark DataFrame, dựa trên nội dung slide bạn cung cấp. Tài liệu được trình bày dưới dạng Markdown chuyên nghiệp, tập trung vào góc độ kỹ thuật Big Data và Hệ thống Phân tán.

---

# Apache Spark: DataFrame, Transformations, Actions và Caching

## 1. Tổng quan về Mô hình Lập trình (Programming Model)

Apache Spark sử dụng một mô hình lập trình dựa trên **RDD (Resilient Distributed Dataset)** hoặc **DataFrame** (một RDD có cấu trúc). Điểm đặc biệt của Spark là mô hình **Lazy Evaluation** (Thực thi trì hoãn).

*   **Transformations:** Các thao tác biến đổi dữ liệu (như filter, map, distinct). Chúng không thực thi ngay lập tức mà chỉ xây dựng một **Execution Plan** (Kế hoạch thực thi).
*   **Actions:** Các lệnh yêu cầu Spark thực thi kế hoạch đã xây dựng và trả về kết quả cho Driver hoặc lưu xuống đĩa.

---

## 2. Transformations (Biến đổi)

**Khái niệm:**
Transformations là các thao tác tạo ra một DataFrame mới từ một DataFrame hiện có. Các thao tác này **không thực thi ngay lập tức** mà chỉ được ghi nhận lại trong DAG (Directed Acyclic Graph) cho đến khi một Action được gọi.

### Ví dụ từ Slide & Code Mẫu

Nội dung slide minh họa quy trình tạo DataFrame, loại bỏ trùng lặp và sắp xếp.

**Dữ liệu đầu vào:**
```python
data = [('Alice', 1), ('Bob', 2), ('Bob', 2)]
```

**Code Python hoàn chỉnh (PySpark):**

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Khởi tạo Spark Session
spark = SparkSession.builder.appName("TransformationExample").getOrCreate()

# 1. Tạo DataFrame (Tương đương sqlContext.createDataFrame)
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])
df1 = spark.createDataFrame(data, schema)

# 2. Transformation: distinct() - Loại bỏ các bản ghi trùng lặp
# ('Bob', 2) xuất hiện 2 lần, nhưng df2 chỉ chứa 1 lần.
df2 = df1.distinct()

# 3. Transformation: sort() - Sắp xếp giảm dần theo cột 'age'
df3 = df2.sort("age", ascending=False)

# KẾT QUẢ DỰ KIẾN (Sau khi gọi Action):
# df3 sẽ chứa: 
# Row(name='Bob', age=2)
# Row(name='Alice', age=1)
```

### Giải thích chi tiết các thao tác:
*   `createDataFrame`: Chuyển đổi một collection (list, tuple) hoặc RDD thành DataFrame với schema định nghĩa rõ ràng.
*   `distinct()`: Loại bỏ các hàng trùng lặp hoàn toàn. Đây là một thao tác shuffle (phân phối lại dữ liệu giữa các node).
*   `sort("age", ascending=False)`: Sắp xếp dữ liệu theo cột `age` giảm dần.

---

## 3. Actions (Hành động)

**Khái niệm:**
Actions là các lệnh **kích hoạt việc thực thi** toàn bộ chuỗi Transformations đã tạo ra trước đó. Actions thường trả về kết quả về cho Driver program (thay vì trả về một DataFrame mới).

### Bảng Actions phổ biến

| Action | Mô tả (Description) | Khi nào sử dụng? |
| :--- | :--- | :--- |
| **`show(n, truncate=True)` | In ra `n` dòng đầu tiên của DataFrame lên console. Dùng để xem trước dữ liệu (Preview). | Khi debug hoặc kiểm tra cấu trúc dữ liệu nhanh. |
| **`take(n)` | Lấy `n` dòng đầu tiên dưới dạng danh sách (List of Row). | Khi cần lấy một phần dữ liệu nhỏ để xử lý logic phức tạp ở Driver. |
| **`collect()` | Trả về **tất cả** các bản ghi dưới dạng List về Driver. | **Cẩn thận:** Chỉ dùng với dữ liệu nhỏ. Gây tràn bộ nhớ Driver nếu dữ liệu lớn. |
| **`count()` | Đếm và trả về tổng số dòng trong DataFrame. | Kiểm tra quy mô dữ liệu, validate sau khi filter. |
| **`describe(*cols)` | Phân tích thống kê mô tả (EDA): Đếm, Trung bình, Đô lệch chuẩn (stddev), Min, Max. | Khai phá dữ liệu (EDA) để hiểu phân bố dữ liệu các cột số. |

### Ví dụ sử dụng Actions

**Code Python:**

```python
# Tạo DataFrame mẫu
data = [('Alice', 1), ('Bob', 2)]
df = spark.createDataFrame(data, ['name', 'age'])

# 1. collect()
# Kết quả: [Row(name='Alice', age=1), Row(name='Bob', age=2)]
all_rows = df.collect()
print(f"Collect: {all_rows}")

# 2. count()
# Kết quả: 2
row_count = df.count()
print(f"Count: {row_count}")

# 3. show()
# In ra bảng đẹp mắt trên console
print("Show output:")
df.show()
# Output:
# +------+---+
# |  name|age|
# +------+---+
# |Alice |  1|
# |Bob   |  2|
# +------+---+

# 4. describe()
# Thống kê cột age
df.describe("age").show()
```

---

## 4. Caching (Bộ nhớ đệm)

**Khái niệm:**
**Caching** (hoặc `persist`) là kỹ thuật lưu trữ tạm thời DataFrame/RDD vào bộ nhớ (Memory) của các worker nodes trong cluster. Điều này giúp tăng tốc độ truy xuất dữ liệu trong các tác vụ lặp lại (iterative algorithms) hoặc khi một DataFrame được sử dụng làm nguồn cho nhiều Action khác nhau.

### Ví dụ từ Slide & Code Mẫu

Slide minh họa việc đọc file, cache dữ liệu gốc, lọc dữ liệu và cache tiếp dữ liệu đã lọc.

**Code Python:**

```python
from pyspark.sql.functions import col

# Giả lập đọc file text
# linesDF = spark.read.text("path/to/log_file.txt")

# Tạo dữ liệu mẫu cho ví dụ
data_logs = [
    ("INFO: System start",), 
    ("DEBUG: Check connection",), 
    ("ERROR: DB connection failed",),
    ("INFO: User login",)
]
linesDF = spark.createDataFrame(data_logs, ["line"])

# 1. Cache linesDF
# Dữ liệu gốc được giữ trong RAM để tránh đọc lại từ disk hoặc tính toán lại.
linesDF.cache()

# 2. Tạo DataFrame mới từ linesDF (Transformation)
# Lọc các dòng bắt đầu bằng 'INFO' hoặc 'ERROR'
# Giả lập hàm isComment (filter logic)
commentsDF = linesDF.filter(
    (col("line").startswith("INFO")) | (col("line").startswith("ERROR"))
)

# 3. Thực thi Actions
# linesDF.count() sẽ đọc dữ liệu và cache nó.
# commentsDF.count() sẽ thực thi filter và cache kết quả (nếu gọi .cache() cho nó).
print(f"Lines count: {linesDF.count()}") 
# commentsDF.cache() # Bỏ comment dòng này nếu muốn cache kết quả lọc
print(f"Comments count: {commentsDF.count()}")

# Kiểm tra lại (Lúc này dữ liệu được lấy từ Cache, rất nhanh)
print(f"Lines count again (from cache): {linesDF.count()}")
```

### Tại sao phải dùng Caching?
*   **Problem:** Nếu bạn thực thi `linesDF.count()` và sau đó `commentsDF.count()`, Spark sẽ thực thi lại pipeline `read -> filter` từ đầu cho `commentsDF`.
*   **Solution:** `linesDF.cache()` giữ dữ liệu gốc trong RAM. Khi `commentsDF` được tạo ra, nó trỏ đến vùng nhớ cache đó, giúp tiết kiệm thời gian I/O.

---

## 5. Quy trình Lập trình Tiêu chuẩn (Standard Workflow)

Để tối ưu hóa hiệu năng khi làm việc với Spark DataFrame, bạn nên tuân thủ quy trình 4 bước sau:

### Bước 1: Khởi tạo & Nhập liệu (Create)
Từ dữ liệu外部 (External) hoặc từ biến nội bộ (Driver collection).
*   *Thao tác:* `spark.read...` hoặc `spark.createDataFrame(...)`

### Bước 2: Biến đổi (Transform)
Xây dựng các chuỗi thao tác清洗, chuyển đổi dữ liệu.
*   *Thao tác:* `filter`, `select`, `groupBy`, `withColumn`, `distinct`...
*   *Lưu ý:* Dữ liệu chưa được tính toán ở bước này.

### Bước 3: Tối ưu hóa (Optimize & Cache)
Nếu DataFrame中间 kết quả được sử dụng nhiều lần, hãy cache nó.
*   *Thao tác:* `df.cache()` hoặc `df.persist()`

### Bước 4: Thực thi & Xuất kết quả (Action)
Kích hoạt pipeline để tính toán và nhận kết quả.
*   *Thao tác:* `df.show()`, `df.write.save(...)`, `df.collect()`

---

## 6. Ưu & Nhược điểm của Mô hình Spark DataFrame

| Tiêu chí | Chi tiết |
| :--- | :--- |
| **Ưu điểm (Pros)** | **Tối ưu hóa tự động (Tungsten Engine):** Spark tự động tối ưu hóa kế hoạch thực thi (logical/physical plan).<br>**Lazy Evaluation:** Giúp tránh các thao tác không cần thiết và tối ưu hóa luồng dữ liệu (pipelines).<br>**API đa dạng:** Hỗ trợ SQL, Python, Scala, Java.<br>**Tích hợp Caching:** Dễ dàng tăng tốc độ xử lý lặp lại. |
| **Nhược điểm (Cons)** | **Khó Debug:** Do trì hoãn thực thi, lỗi thường chỉ xuất hiện khi gọi Action.<br>**Bộ nhớ Driver:** `collect()` có thể gây crash Driver nếu dữ liệu trả về quá lớn.<br>**Overhead nhỏ:** So với RDD thuần, DataFrame có một chút overhead về việc tạo đối tượng Row. |

---

## 7. Ví dụ Thực tế trong Ngành (Industry Use Cases)

### Case 1: ETL (Extract, Transform, Load) trong Banking
*   **Scenario:** Ngân hàng cần xử lý 10TB dữ liệu giao dịch mỗi ngày để tính toán số dư cuối ngày.
*   **Application:**
    1.  **Create:** Đọc dữ liệu giao dịch từ Data Lake (S3/HDFS).
    2.  **Transform:** `filter` các giao dịch hợp lệ, `groupBy` theo `account_id` và `sum` số tiền.
    3.  **Cache:** Nếu cần tính toán thêm phí giao dịch dựa trên số dư, cache kết quả `groupBy` lại.
    4.  **Action:** Ghi kết quả vào Data Warehouse (Hive/Redshift).

### Case 2: Phân tích Log hệ thống (Real-time Monitoring)
*   **Scenario:** Phân tích log server để tìm lỗi (Error) phát sinh trong 1 giờ qua.
*   **Application:**
    1.  **Create:** Đọc file log stream hoặc batch.
    2.  **Transform:** `filter` dòng có chứa từ khóa "ERROR", `select` lấy timestamp và message.
    3.  **Action:** `df.show(10)` để xem lỗi gần nhất, hoặc `df.count()` để alert nếu số lỗi > ngưỡng cho phép.

---

Chào bạn, tôi là chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết về nội dung slide liên quan đến **Apache Spark MLlib**, được trình bày một cách chuyên nghiệp và cấu trúc rõ ràng theo yêu cầu của bạn.

---

# Apache Spark MLlib: Phân tích và Hướng dẫn Chi tiết

Apache Spark MLlib là một thư viện Machine Learning (ML) được xây dựng trên nền tảng Spark, nhằm hỗ trợ các lập trình viên thực hiện các tác vụ ML trên các tập dữ liệu lớn (Big Data) một cách hiệu quả. MLlib cung cấp hai API chính: `spark.mllib` (dựa trên RDD) và `spark.ml` (dựa trên DataFrame). Trong phạm vi bài viết này, chúng ta tập trung vào **Spark ML (DataFrame-based API)** vì đây là API chính được khuyến khích sử dụng hiện nay.

## 1. Tổng quan về MLlib

MLlib cung cấp một bộ công cụ toàn diện để xây dựng các pipeline học máy, từ tiền xử lý dữ liệu đến huấn luyện mô hình và đánh giá.

### Các giải thuật học máy (Machine Learning Algorithms)
MLlib bao gồm các thuật toán phổ biến để giải quyết các bài toán:
*   **Phân loại (Classification):** Logistic Regression, Decision Trees, Random Forests, Gradient-Boosted Trees, Naive Bayes.
*   **Hồi quy (Regression):** Linear Regression, Generalized Linear Regression, Survival Regression.
*   **Phân cụm (Clustering):** K-means, Gaussian Mixture Models, Bisecting K-means, Latent Dirichlet Allocation (LDA).
*   **Lọc cộng tác (Collaborative Filtering):** Alternating Least Squares (ALS).

### Xây dựng đặc trưng (Featurization)
Đây là quá trình biến đổi dữ liệu thô thành các vector số mà máy tính có thể hiểu được.
*   **Trích rút, biến đổi (Extraction, Transformation):** Chuyển đổi văn bản thành vector, xử lý các giá trị còn thiếu.
*   **Giảm chiều (Dimensionality Reduction):** PCA (Principal Component Analysis), SVD (Singular Value Decomposition) để giảm số lượng đặc trưng mà vẫn giữ được thông tin quan trọng.
*   **Lựa chọn đặc trưng (Feature Selection):** Chi-Squared test, VectorSlicer.

### Các tiện ích (Utilities)
*   **Đại số tuyến tính (Linear Algebra):** Các lớp vector và ma trận cơ bản.
*   **Thống kê (Statistics):** Tính toán mean, variance, correlation, chi-square.

---

## 2. Các Khái niệm Lõi trong Spark ML

Spark ML sử dụng các khái niệm abstraction (trừu tượng) để chuẩn hóa quy trình làm việc. Ba thành phần chính là **Transformer**, **Estimator**, và **Pipeline**.

### A. Transformer

**Khái niệm:**
Một `Transformer` là một thuật toán có thể biến đổi một DataFrame thành một DataFrame khác. Nó không thay đổi dữ liệu gốc mà tạo ra một cột mới chứa kết quả dự đoán hoặc biến đổi. Hầu hết các Transformer hoạt động theo cơ chế "append" (thêm cột) hoặc "replace" (thay thế cột).

**Phương thức chính:** `transform()`

**Ví dụ các Transformer:**
*   **HashingTF:** Chuyển đổi một cột văn bản thành một vector tần suất (Term Frequency).
*   **Binarizer:** Chuyển đổi các giá trị số liên tục thành nhị phân (0 hoặc 1) dựa trên ngưỡng.
*   **LogisticRegressionModel:** Sau khi được huấn luyện, nó là một Transformer có thể dùng để dự đoán nhãn mới.

**Code Mẫu (Minh họa Transformer):**

```python
from pyspark.ml.feature import Binarizer

# Giả sử DataFrame 'df' có cột 'score' với giá trị từ 0.0 đến 1.0
# Chúng ta muốn chuyển đổi score thành 0 (nếu < 0.5) và 1 (nếu >= 0.5)

# Khởi tạo Binarizer
binarizer = Binarizer(
    inputCol="score",      # Cột đầu vào
    outputCol="pass_fail", # Cột đầu ra
    threshold=0.5          # Ngưỡng
)

# Áp dụng transform
binarized_df = binarizer.transform(df)
binarized_df.show()
```

### B. Estimator

**Khái niệm:**
Một `Estimator` là một thuật toán học (learning algorithm) được dùng để huấn luyện trên dữ liệu. Nó lấy một DataFrame làm đầu vào và tạo ra một `Transformer` (thường là một Model). Quá trình này gọi là "fitting".

**Phương thức chính:** `fit()`

**Ví dụ các Estimator:**
*   **LogisticRegression:** Thuật toán học Logistic Regression.
*   **StandardScaler:** Thuật toán tính toán mean và standard deviation để chuẩn hóa dữ liệu.
*   **Pipeline:** Một Estimator bao gồm nhiều stage.

**Code Mẫu (Minh họa Estimator):**

```python
from pyspark.ml.classification import LogisticRegression

# Dữ liệu huấn luyện (Training Data)
# (label, features) là 2 cột bắt buộc
training_data = spark.createDataFrame([
    (1.0, Vectors.dense([0.0, 1.1, 0.1])),
    (0.0, Vectors.dense([2.0, 1.0, -1.0])),
    (0.0, Vectors.dense([2.0, 1.3, 1.0])),
    (1.0, Vectors.dense([0.0, 1.2, -0.5]))
], ["label", "features"])

# Khởi tạo Estimator
lr = LogisticRegression(maxIter=10, regParam=0.01)

# Gọi phương thức fit() để tạo ra một Transformer (Model)
model = lr.fit(training_data)

# 'model' bây giờ là một LogisticRegressionModel (Transformer)
print(model.coefficients)
print(model.intercept)
```

### C. Pipeline

**Khái niệm:**
`Pipeline` là một lớp đặc biệt, nó đóng vai trò là một **Estimator** nhưng chứa một chuỗi các **stage** (các Transformer hoặc Estimator khác). Pipeline cho phép ta xếp các bước xử lý dữ liệu và huấn luyện mô hình thành một luồng duy nhất.

**Cơ chế hoạt động:**
1.  Đầu vào của Stage này là đầu ra của Stage trước.
2.  Khi `Pipeline.fit()` được gọi, các stage được thực hiện theo thứ tự.
3.  Nếu một stage là `Estimator`, nó sẽ được huấn luyện (`fit`) và sinh ra một `Transformer` để dùng cho các stage tiếp theo hoặc cho việc dự đoán sau này.

**Code Mẫu (Minh họa Pipeline):**

```python
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer

# 1. Chuẩn bị dữ liệu
training_df = spark.createDataFrame([
    (0, "a b c d e spark", 1.0),
    (1, "b d", 0.0),
    (2, "spark f g h", 1.0),
    (3, "hadoop mapreduce", 0.0)
], ["id", "text", "label"])

# 2. Định nghĩa các stage của Pipeline
# Stage 1: Tokenizer (Transformer) - Tách câu thành từ
tokenizer = Tokenizer(inputCol="text", outputCol="words")

# Stage 2: HashingTF (Transformer) - Chuyển từ thành vector số
hashingTF = HashingTF(inputCol="words", outputCol="features", numFeatures=20)

# Stage 3: LogisticRegression (Estimator) - Mô hình học
lr = LogisticRegression(maxIter=10, regParam=0.001)

# 3. Xếp các stage vào Pipeline
pipeline = Pipeline(stages=[tokenizer, hashingTF, lr])

# 4. Huấn luyện Pipeline (Tạo ra PipelineModel)
pipeline_model = pipeline.fit(training_df)

# 'pipeline_model' bây giờ là một PipelineModel (Transformer)
# Nó có thể dùng để dự đoán trên dữ liệu mới
test_df = spark.createDataFrame([
    (4, "spark i j k"),
    (5, "l m n"),
    (6, "mapreduce spark"),
    (7, "apache hadoop")
], ["id", "text"])

predictions = pipeline_model.transform(test_df)
predictions.select("id", "text", "probability", "prediction").show()
```

### D. PipelineModel

**Khái niệm:**
`PipelineModel` là kết quả trả về của phương thức `Pipeline.fit()`. Nó là một **Transformer**, nghĩa là nó có phương thức `transform()`. Khi bạn đã có `PipelineModel`, bạn có thể dùng nó để xử lý dữ liệu mới (test data hoặc production data) mà không cần phải huấn luyện lại các mô hình bên trong.

**Sự khác biệt:**
*   `Pipeline` (Estimator): Dùng để huấn luyện (Training phase).
*   `PipelineModel` (Transformer): Dùng để dự đoán (Prediction/Inference phase).

---

## 3. Hướng dẫn Sử dụng & Phân tích Ưu/Nhược điểm

### Khi nào sử dụng Spark MLlib?
*   **Dữ liệu lớn (Big Data):** Khi dữ liệu của bạn không thể fit vào RAM của một máy đơn (Single Node) và cần xử lý phân tán.
*   **Streaming Data:** Khi kết hợp với Spark Streaming để xử lý dữ liệu realtime.
*   **Xây dựng ETL + ML:** Khi bạn cần tiền xử lý dữ liệu phức tạp (ETL) và huấn luyện mô hình trong cùng một pipeline.

### Sử dụng như thế nào? (Workflow)
1.  **Prepare Data:** Tạo DataFrame, xử lý missing values.
2.  **Define Pipeline:** Xác định các bước tiền xử lý (Feature Engineering) và thuật toán (Algorithm).
3.  **Fit:** Chạy `pipeline.fit(training_data)` để tạo `PipelineModel`.
4.  **Transform:** Chạy `model.transform(test_data)` để lấy kết quả dự đoán.
5.  **Tuning:** Sử dụng `CrossValidator` hoặc `TrainValidationSplit` để tìm siêu tham số (Hyperparameter) tốt nhất.

### Ưu & Nhược điểm

| Tiêu chí | Chi tiết |
| :--- | :--- |
| **Ưu điểm (Pros)** | **Tính toán phân tán:** Khả năng mở rộng (Scalability) cực tốt trên các cụm Cluster.<br>**API thống nhất:** `Transformer` và `Estimator` giúp code dễ đọc, dễ bảo trì.<br>**Tích hợp sẵn:** Hoạt động tốt với Spark SQL và Hive.<br>**Pipeline:** Rất mạnh mẽ trong việc tự động hóa quy trình ML. |
| **Nhược điểm (Cons)** | **Độ sâu thuật toán:** Các thuật toán trong MLlib thường đơn giản hơn so với Scikit-learn hay TensorFlow (ví dụ: Neural Network còn hạn chế).<br>**Tuning phức tạp:** Tuning hyperparameter trên Cluster thường chậm hơn so với Local.<br>**Lỗi cú pháp:** Lỗi trong Pipeline (như sai tên cột) thường chỉ phát hiện khi chạy (Runtime error). |

---

## 4. Ví dụ Thực tế trong Công nghiệp

### Bài toán: Ngân hàng dự đoán rủi ro tín dụng (Credit Risk Scoring)

**Scenario:** Một ngân hàng có hàng triệu dữ liệu hồ sơ vay vốn. Họ cần xây dựng hệ thống tự động để dự đoán xem một khách hàng mới có khả năng trả nợ hay không (Default vs. Non-Default).

**Cách áp dụng Spark ML:**

1.  **Dữ liệu (Data):**
    *   `customer_id`: ID khách hàng.
    *   `income`: Thu nhập.
    *   `loan_amount`: Số tiền vay.
    *   `credit_history`: Lịch sử tín dụng (dạng text hoặc số).
    *   `label`: 1 (Trả nợ tốt), 0 (Nợ xấu).

2.  **Pipeline Design:**
    *   **Stage 1 (VectorAssembler):** Gộp các cột `income`, `loan_amount` thành một cột vector `features`.
    *   **Stage 2 (StandardScaler):** Chuẩn hóa các đặc trưng để thuật toán chạy ổn định hơn.
    *   **Stage 3 (RandomForestClassifier):** Huấn luyện mô hình Random Forest.

3.  **Execution:**
    *   Chạy `pipeline.fit(training_data)` trên cluster (ví dụ: AWS EMR hoặc Databricks).
    *   Lưu `PipelineModel` xuống HDFS/S3.

4.  **Prediction:**
    *   Khi có hồ sơ mới, hệ thống tải `PipelineModel` và gọi `transform()` để trả về xác suất rủi ro ngay lập tức.

**Lợi ích:** Xử lý hàng loạt hàng triệu hồ sơ nhanh chóng, khả năng mở rộng khi dữ liệu tăng, và dễ dàng cập nhật mô hình khi có dữ liệu mới.

---

Chào bạn, tôi là một chuyên gia về Big Data và Hệ thống Phân tán. Dưới đây là phân tích chi tiết và trình bày lại nội dung từ tài liệu slide "7_apache_spark.pdf" theo yêu cầu của bạn.

---

# Apache Spark: Kiến Trúc và Phân Tích Tính Toán Phân Tán

Tài liệu này cung cấp cái nhìn tổng quan về kiến trúc của Apache Spark, cách nó thực thi các công việc, và các khái niệm cốt lõi về biến đổi dữ liệu (Transformations).

## 1. Kiến Trúc Tổng Quan (General Architecture)

Apache Spark được thiết kế dựa trên mô hình **Master-Worker**, một kiến trúc phổ biến trong các hệ thống phân tán.

### Giải thích Khái niệm
- **Master (Driver Node):** Đây là "bộ não" của ứng dụng Spark. Nó chịu trách nhiệm chạy hàm `main()`, tạo `SparkContext`, và lập kế hoạch thực thi các tác vụ.
- **Worker Nodes:** Các node thực thi công việc. Mỗi worker có thể chạy nhiều **Executor** (đơn vị tính toán).
- **Công việc (Jobs):** Master sẽ chia nhỏ một chương trình thành các tác vụ và gửi chúng đến các Worker.
- **Dữ liệu (Data Sources):** Worker có thể lấy dữ liệu từ bộ nhớ trong (In-memory) hoặc từ các hệ thống lưu trữ bên ngoài như **HDFS** (Hadoop Distributed File System) hoặc **Amazon S3**.

### Ưu & Nhược điểm
| Tiêu chí | Chi tiết |
| :--- | :--- |
| **Ưu điểm** | - **Tính chịu lỗi cao (Fault Tolerance):** Nếu một Worker chết, Master sẽ giao lại tác vụ cho Worker khác.<br>- **Mở rộng quy mô (Scalability):** Dễ dàng thêm Worker Node để tăng năng lực tính toán.<br>- **Tối ưu hóa:** Master lên kế hoạch thực thi tối ưu (Query Optimization). |
| **Nhược điểm** | - **Độ phức tạp của cài đặt:** Cần cấu hình mạng, quản lý tài nguyên (YARN/Mesos).<br>- **Single Point of Failure (SPOF):** Driver (Master) nếu gặp lỗi thì toàn bộ job dừng lại (trừ khi dùng chế độ High Availability). |

### Ví dụ Thực tế
Trong một công ty thương mại điện tử, **Driver Node** nhận yêu cầu phân tích hành vi người dùng trong ngày. Nó truy vấn dữ liệu giao dịch từ **HDFS**, chia nhỏ công việc và gửi đến 100 **Worker Nodes**. Mỗi Worker xử lý 1% dữ liệu và trả kết quả về Driver.

---

## 2. SparkContext và Cấu Hình Cụm (Cluster)

Mọi chương trình Spark đều bắt đầu bằng việc khởi tạo một đối tượng `SparkContext`.

### Giải thích Khái niệm
`SparkContext` đại diện cho kết nối đến một cụm Spark cluster. Nó cho phép Spark biết cách sử dụng tài nguyên (CPU, RAM) và nơi để chạy các tác vụ.

### Các tham số cấu hình (Master Parameters)
Khi khởi tạo `SparkContext`, bạn cần chỉ định URL của Master (hoặc chế độ chạy).

| Tham số (Master) | Mô tả | Khi nào sử dụng? |
| :--- | :--- | :--- |
| **`local`** | Chạy trên một máy cục bộ, sử dụng **1 luồng** xử lý. | Gỡ lỗi (Debug) đơn giản, chạy thử nghiệm nhỏ. |
| **`local[K]`** | Chạy trên máy cục bộ, sử dụng **K luồng** xử lý song song. | Tối ưu hóa trên máy cá nhân, xử lý dữ liệu vừa phải (VD: `local[4]` cho CPU 4 nhân). |
| **`spark://HOST:PORT`** | Kết nối đến **Spark Standalone Cluster** (cụm Spark tự quản lý). | Khi bạn tự cài đặt và quản lý cluster (không dùng Hadoop YARN). |
| **`mesos://HOST:PORT`** | Kết nối đến **Apache Mesos** cluster. | Cụm Mesos đang quản lý tài nguyên (hiện ít phổ biến hơn YARN/Kubernetes). |
| **`yarn`** | Kết nối đến **Hadoop YARN** cluster. | Phổ biến nhất trong doanh nghiệp lớn khi đã dùng Hadoop Ecosystem. |

### Code Mẫu (PySpark)

```python
from pyspark import SparkContext, SparkConf

# Cấu hình ứng dụng
conf = SparkConf().setAppName("MyFirstSparkApp").setMaster("local[4]")

# Khởi tạo SparkContext
sc = SparkContext(conf=conf)

# Kiểm tra thông tin Context
print(sc.version)
print(sc.appName)

# Dừng Context khi xong việc
# sc.stop()
```

---

## 3. Chu Trình Một Công Việc (Job Execution Cycle)

Một chương trình Spark không chạy tuần tự như Python thông thường. Nó hoạt động theo mô hình **Lazy Evaluation** (Tính toán trễ).

### Quy trình thực thi:
1.  **Tạo SparkContext:** Khởi tạo kết nối.
2.  **Đọc Dữ liệu (RDD/DataFrame):** Tạo tập dữ liệu ban đầu từ nguồn (File, DB...).
3.  **Áp dụng Transformations:** Các lệnh như `map`, `filter`, `groupBy`. **Lưu ý:** Lúc này Spark chưa chạy tính toán ngay, nó chỉ ghi lại "kế hoạch" (Lineage).
4.  **Áp dụng Action:** Các lệnh như `count`, `collect`, `saveAsTextFile`. Khi gặp Action, Spark mới bắt đầu tối ưu hóa và thực thi các Transformations đã tích lũy.
5.  **Trả kết quả:** Driver trả kết quả về hoặc lưu dữ liệu ra storage.

---

## 4. Biến Dữ Liệu (Transformations): Narrow vs Wide

Đây là khái niệm cốt lõi quyết định hiệu năng của Spark. Các thao tác biến đổi dữ liệu được chia làm 2 loại dựa trên cách dữ liệu di chuyển giữa các **Partitions**.

### A. Narrow Transformation
* **Định nghĩa:** Mỗi partition dữ liệu đầu vào chỉ ảnh hưởng đến một (hoặc rất ít) partition dữ liệu đầu ra. Dữ liệu **không cần phải shuffle** (phân tán lại) giữa các node.
* **Tốc độ:** Rất nhanh, có thể thực hiện pipelining (xử lý nối tiếp ngay trên worker đó).

### B. Wide Transformation (Shuffle)
* **Định nghĩa:** Một partition dữ liệu đầu vào có thể ảnh hưởng đến **nhiều** partition dữ liệu đầu ra. Để thực hiện, Spark phải đọc dữ liệu từ nhiều worker, gom lại, sắp xếp lại (Sort/Reduce), rồi gửi đi các worker khác.
* **Tốc độ:** Chậm, tốn tài nguyên I/O và mạng.

### Bảng So Sánh

| Đặc điểm | Narrow Transformation | Wide Transformation |
| :--- | :--- | :--- |
| **Ví dụ** | `map()`, `filter()`, `union()`, `project()` | `reduceByKey()`, `groupByKey()`, `join()`, `distinct()` |
| **Dữ liệu** | Độc lập (Independence) | Phụ thuộc (Dependency) |
| **Shuffle** | Không | Có (Bắt buộc) |
| **Chi phí** | Thấp | Cao |

### Code Mẫu Minh Hoạ

```python
# Giả sử data là một RDD chứa các dòng text
data = sc.parallelize(["hello world", "hello spark", "big data"], 2)

# --- NARROW TRANSFORMATION ---
# Filter: Mỗi partition được lọc độc lập, không cần trao đổi data
filtered_data = data.filter(lambda line: "spark" in line)
# Kết quả: ["hello spark"]

# Map: Ánh xạ từng phần tử độc lập
mapped_data = data.map(lambda line: line.split(" "))
# Kết quả: [["hello", "world"], ["hello", "spark"], ["big", "data"]]

# --- WIDE TRANSFORMATION ---
# ReduceByKey: Cần gom tất cả các từ "hello" lại với nhau dù chúng ở partition nào
# Phải Shuffle dữ liệu
word_counts = data.flatMap(lambda line: line.split(" ")) \
                  .map(lambda word: (word, 1)) \
                  .reduceByKey(lambda a, b: a + b)
# Kết quả: [('hello', 2), ('world', 1), ('spark', 1), ('big', 1), ('data', 1)]
```

---

## 5. Mối Quan Hệ Giữa Transformations và Stages

Spark không chạy từng dòng code một cách máy móc mà nó tối ưu hóa thành các **Stages** (Giai đoạn).

### Giải thích Khái niệm
- **Stage:** Một giai đoạn tính toán, chứa các tác vụ có thể chạy song song mà không cần shuffle.
- **Pipeline:** Các Narrow Transformations có thể được gom vào cùng một Stage và thực thi liên tục trên bộ nhớ (In-memory pipeline) mà không cần ghi tạm dữ liệu ra đĩa.

### Quy tắc gom Stage
- **Narrow Transformation:** Các phép biến đổi này được nhóm lại với nhau trong **cùng một Stage**.
- **Wide Transformation (Shuffle):** Đây là ranh giới giữa các Stage. Khi gặp Wide Transformation, Spark sẽ kết thúc Stage hiện tại và bắt đầu một Stage mới.

### Minh Hoạ Quy Trình
Giả sử bạn có chuỗi lệnh:
`Read -> Map -> Filter -> ReduceByKey -> Map`

1.  **Stage 1:**
    *   `Read` (Đọc dữ liệu)
    *   `Map` (Narrow)
    *   `Filter` (Narrow)
    *   *(Gom lại, xử lý nhanh)*
2.  **Ranh giới Shuffle** (Do `ReduceByKey`)
3.  **Stage 2:**
    *   `ReduceByKey` (Wide - Shuffle)
    *   `Map` (Narrow trên dữ liệu đã gom)

### Ví dụ Thực tế trong Industry
Trong hệ thống Recommendation Engine (Gợi ý sản phẩm):
*   **Stage 1 (Narrow):** Lọc các giao dịch không hợp lệ và ánh xạ sang (UserID, ProductID). Các thao tác này chạy rất nhanh trên từng node.
*   **Stage 2 (Wide):** Tính toán ma trận tương đồng (Collaborative Filtering). Node A cần biết Node B đã mua gì để tính toán độ tương đồng. Đây là bước Shuffle tốn kém nhất, thường được tối ưu hóa bằng cách tăng số lượng partition hoặc dùng kỹ thuật Broadcast Join.

---

## Tóm tắt Phân tích cho người mới bắt đầu

1.  **Luôn nhớ `SparkContext`:** Cổng kết nối của bạn với Cluster.
2.  **Chọn `local[K]` cho máy yếu:** Đừng để `local` (1 core) nếu máy bạn có 8 core.
3.  **Tối ưu Narrow:** Càng nhiều Narrow Transformation, Spark chạy càng nhanh.
4.  **Cẩn trọng với Wide:** `groupByKey` hay `reduceByKey` là nguyên nhân gây treo (Hang) và chạy chậm trong Spark. Hãy cố gắng lọc dữ liệu (`filter`) trước khi thực hiện Wide Transformation.

---

Chào bạn, tôi là một chuyên gia về Big Data và Hệ thống Phân tán. Dựa trên nội dung tóm tắt cuối cùng của tài liệu slide "7_apache_spark.pdf", tôi sẽ phân tích và trình bày chi tiết các khái niệm **Hadoop** và **Spark** một cách chuyên sâu, đáp ứng tất cả các yêu cầu bạn đưa ra.

---

# Tổng Quan về Hadoop và Apache Spark

Tài liệu slide kết luận bằng việc định vị hai công nghệ cốt lõi trong hệ sinh thái Big Data: **Hadoop** (vai trò lưu trữ và xử lý kinh tế) và **Spark** (vai trò phân tích dữ liệu hợp nhất, tốc độ cao). Dưới đây là phân tích chi tiết.

---

## 1. Apache Hadoop

**Hadoop** là một khuôn khổ phần mềm mã nguồn mở cho phép lưu trữ và xử lý các tập dữ liệu lớn (Big Data) trong môi trường phân tán. Nó được thiết kế để mở rộng từ một máy chủ đơn lẻ lên hàng nghìn máy, mỗi máy cung cấp khả năng lưu trữ và tính toán cục bộ.

### Giải thích Khái niệm
Hadoop hoạt động dựa trên nguyên lý "Move Computation to Data" (Mang điện toán đến dữ liệu) thay vì mang dữ liệu đến điện toán. Nó bao gồm các module chính:
*   **Hadoop Distributed File System (HDFS):** Hệ thống file phân tán để lưu trữ dữ liệu khổng lồ.
*   **MapReduce:** Mô hình lập trình để xử lý dữ liệu song song hàng loạt (Batch Processing).

### Khi nào sử dụng? (Use Cases)
*   **Lưu trữ kho dữ liệu (Data Lake):** Khi bạn cần lưu trữ lượng dữ liệu phi cấu trúc hoặc bán cấu trúc khổng lồ (log files, sensor data) với chi phí thấp.
*   **Xử lý Batch:** Các tác vụ xử lý dữ liệu định kỳ, không cần thời gian thực (ví dụ: xử lý hóa đơn cuối ngày, phân tích nhật ký server hàng giờ).
*   **Lưu trữ giá rẻ:** Khi chi phí phần cứng là yếu tố quan trọng và bạn cần dung lượng lưu trữ petabyte.

### Sử dụng như thế nào? (How to use)
1.  **Cài đặt Cluster:** Thiết lập các node Master (NameNode, ResourceManager) và Worker (DataNode, NodeManager).
2.  **Lưu trữ:** Đẩy dữ liệu lên HDFS bằng lệnh `hdfs dfs -put`.
3.  **Xử lý:** Viết job MapReduce (thường dùng Java hoặc Python via Hadoop Streaming) hoặc dùng các công cụ cao cấp hơn như Hive/Pig trên nền tảng YARN.

### Ưu & Nhược điểm

| Tiêu chí | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- |
| **Khả mở (Scalability)** | Có thể mở rộng lên hàng nghìn node. | Phức tạp trong quản lý cluster lớn. |
| **Chi phí (Cost)** | Hoạt động trên phần cứng thương mại (Commodity hardware), rẻ. | Tốn tài nguyên phần cứng để đảm bảo dung lượng lưu trữ. |
| **Tính ổn định** | Rất ổn định cho các tác vụ Batch lớn. | **Latency cao:** Không phù hợp cho xử lý thời gian thực (Real-time). |
| **Lập trình** | Phù hợp cho các tác vụ song song hóa đơn giản. | Model MapReduce cồng kềnh, khó tối ưu hóa cho các thuật toán phức tạp. |

### Ví dụ Thực tế trong Ngành
Một công ty viễn thông sử dụng Hadoop (HDFS + MapReduce/Hive) để lưu trữ hàng tỷ bản ghi cuộc gọi (CDR) mỗi ngày. Vào cuối ngày, hệ thống chạy các job batch để tính cước phí cho khách hàng và tổng hợp báo cáo doanh thu theo vùng.

### Code Mẫu (MapReduce - Pseudo-code)
Dưới đây là ví dụ về một job MapReduce kinh điển (Word Count) bằng Python (Hadoop Streaming):

```python
#!/usr/bin/env python3
# mapper.py
import sys

# Đọc từng dòng từ stdin
for line in sys.stdin:
    line = line.strip()
    words = line.split()
    for word in words:
        # In ra (word, 1) để reducer tổng hợp
        print(f'{word}\t1')

#!/usr/bin/env python3
# reducer.py
import sys

current_word = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    word, count = line.split('\t', 1)
    
    try:
        count = int(count)
    except ValueError:
        continue

    if current_word == word:
        current_count += count
    else:
        if current_word:
            print(f'{current_word}\t{current_count}')
        current_word = word
        current_count = count

if current_word == word:
    print(f'{current_word}\t{current_count}')
```

---

## 2. Apache Spark

**Apache Spark** là một nền tảng điện toán song song tổng quát, nhanh chóng và được thiết kế cho khả năng mở rộng. Nó được xem là người kế nhiệm của MapReduce, cung cấp các API cấp cao và khả năng xử lý dữ liệu nhanh hơn đáng kể.

### Giải thích Khái niệm
Spark cải tiến MapReduce bằng cách sử dụng **Bộ nhớ RAM (In-memory computing)** thay vì phụ thuộc nhiều vào ghi đĩa (Disk I/O). Điều này giúp tăng tốc độ xử lý lên đến 100 lần cho các tác vụ tương tác hoặc thuật toán học máy.
Spark bao gồm các thành phần chính:
*   **Spark Core:** Động cơ cơ bản với RDD (Resilient Distributed Datasets).
*   **Spark SQL:** Xử lý dữ liệu cấu trúc.
*   **Spark Streaming / Structured Streaming:** Xử lý dữ liệu thời gian thực.
*   **MLlib:** Thư viện Machine Learning.
*   **GraphX:** Xử lý đồ thị.

### Khi nào sử dụng? (Use Cases)
*   **Xử lý Real-time (Streaming):** Phân tích log người dùng website theo thời gian thực, xử lý dữ liệu cảm biến (IoT).
*   **Machine Learning:** Các thuật toán lặp đi lặp lại (Iterative algorithms) như Recommendation Systems, Clustering.
*   **Phân tích tương tác (Interactive Analysis):** Phân tích dữ liệu nhanh qua các notebook (Databricks, Jupyter).
*   **ETL复杂 (Complex ETL):** Các tác vụ chuyển đổi dữ liệu phức tạp cần tốc độ cao.

### Sử dụng như thế nào? (How to use)
1.  **Chọn ngôn ngữ:** Viết code bằng Python (PySpark), Scala, Java, hoặc SQL.
2.  **Chọn môi trường:**
    *   **Standalone:** Cài đặt trực tiếp trên cluster.
    *   **YARN/Kubernetes:** Chạy như một application trên hệ thống quản lý cluster có sẵn.
    *   **Databricks/EMR:** Sử dụng dịch vụ managed cloud.
3.  **Lập trình:** Sử dụng DataFrame API (tương tự SQL) hoặc RDD cho các thao tác tùy chỉnh.

### Ưu & Nhược điểm

| Tiêu chí | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- |
| **Tốc độ** | **Rất nhanh:** In-memory computation giúp giảm thời gian xử lý đáng kể. | **Tốn RAM:** Nếu dữ liệu quá lớn so với RAM, hiệu suất có thể giảm sút (spill to disk). |
| **Tính năng** | **Đa dạng:** Hỗ trợ Batch, Streaming, ML, Graph trong cùng một framework. | **Độ phức tạp:** Cấu hình và tối ưu hóa Spark đòi hỏi kiến thức chuyên sâu. |
| **API** | **Thân thiện:** API cao cấp, dễ đọc (đặc biệt là DataFrame/SQL). | **Chi phí bảo trì:** Việc tối ưu bộ nhớ (Memory Management) cần kinh nghiệm. |
| **Khả năng lỗi** | **Fault Tolerance:** Khôi phục lỗi tốt thông qua DAG (Directed Acyclic Graph). | |

### Ví dụ Thực tế trong Ngành
Một công ty thương mại điện tử (E-commerce) sử dụng **Spark Structured Streaming** để xử lý dữ liệu clickstream từ website. Họ phân tích hành vi người dùng đang diễn ra để đưa ra các gợi ý sản phẩm (Recommendation) hoặc phát hiện gian lận thẻ tín dụng ngay lập tức trong phiên mua sắm.

### Code Mẫu (PySpark - Word Count)
So sánh với Hadoop MapReduce, Spark Code ngắn gọn và dễ hiểu hơn rất nhiều:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

# 1. Tạo Spark Session
spark = SparkSession.builder \
    .appName("WordCountSample") \
    .getOrCreate()

# 2. Đọc dữ liệu (có thể từ file text hoặc stream)
lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# 3. Xử lý dữ liệu (Transformation)
words = lines.select(
   explode(
       split(lines.value, " ")
   ).alias("word")
)

# 4. Tính toán & Xuất ra (Action)
wordCounts = words.groupBy("word").count()

query = wordCounts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
```

---

## 3. So sánh và Tóm tắt

Slide đã tóm tắt vai trò của 2 công nghệ này. Để làm rõ hơn:

| Đặc điểm | Hadoop | Apache Spark |
| :--- | :--- | :--- |
| **Mục tiêu chính** | Lưu trữ và xử lý Batch giá rẻ. | Phân tích dữ liệu tốc độ cao, đa năng. |
| **Lưu trữ** | **Bắt buộc** (HDFS hoặc S3). | **Tùy chọn:** Có thể đọc từ HDFS, S3, Kafka, hoặc xử lý trực tiếp trên RAM. |
| **Xử lý** | MapReduce (Disk-based). | In-memory (hoặc Hybrid). |
| **Tốc độ** | Chậm hơn (phù hợp báo cáo định kỳ). | Nhanh hơn (phù hợp học máy & real-time). |

### Kết luận
Trong các hệ thống hiện đại ngày nay, **Hadoop và Spark thường được sử dụng kết hợp**:
*   **Hadoop HDFS/S3** đóng vai trò là **Data Lake** (kho dữ liệu thô) lưu trữ lượng dữ liệu khổng lồ.
*   **Apache Spark** đóng vai trò là **Công cụ điện toán** để trích xuất, xử lý và phân tích dữ liệu từ kho đó một cách nhanh chóng.

---

