# DEVELOPER DECISION GUIDE: Lesson 1 Kotlin basics.pdf



# DEVELOPER DECISION GUIDE: Kotlin Basics
**Khai báo biến và suy diễn kiểu:**
```kotlin
val name = "Alice" // String được suy diễn tự động, không thay đổi được
var age = 25       // Int được suy diễn, có thể thay đổi
age = 26           // Hợp lệ

// val location: String = null // Lỗi biên dịch: Null không được phép
val location: String? = null   // Hợp lệ: Biến có thể null
```

## SECTION 2: DECISION TABLES

### Nhóm dữ liệu: Array vs List

| Tình huống sử dụng | Nên dùng gì | Tại sao (Performance / Mutability) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Cần danh sách cố định, truy cập nhanh theo chỉ số (index), chỉnh sửa phần tử tại chỗ. | **Array (`IntArray`, `Array<String>`)** | **Fixed-size & Mutable**: Cấu trúc bộ nhớ cố định, tối ưu cho truy cập ngẫu nhiên (O(1)). | Quên khởi tạo với số lượng phần tử cố định (ví dụ `IntArray(5)`). |
| Danh sách thông thường, kích thước thay đổi (thêm/xóa), không cần quan tâm chỉ số. | **List (`listOf`)** | **Read-only mặc định**: `listOf` trả về immutable list. Dùng `mutableListOf` nếu cần sửa đổi. An toàn hơn Array. | Cố gắng sửa đổi List trả về từ `listOf()` (sẽ báo lỗi biên dịch). |

## SECTION 4: CODE PATTERNS

### Pattern : Xử lý Logic Nhánh rẽ (If/Else & When)

**Code Demo:**

```kotlin
fun checkAnimalType(animal: String) {
    // Pattern: When (biến thành expression)
    val message = when (animal) {
        "Cat" -> "Meow"
        "Dog" -> "Woof"
        "Cow" -> "Moo"
        else -> "Unknown animal" // Bắt buộc nếu không liệt kê hết
    }
    println(message)
}
```

### Pattern : Vòng lặp và Duyệt Collection

**Khi nào dùng:**
Khi cần xử lý từng phần tử trong danh sách (List/Array).
**Code Demo:**

```kotlin
fun processList() {
    val numbers = listOf(1, 2, 3, 4, 5)

    // Pattern 1: DuyệtforEach
    numbers.forEach { number ->
        println("Number is $number")
    }

    // Pattern 2: Vòng lặp For (truy cập index nếu cần)
    for (i in numbers.indices) {
        if (numbers[i] == 3) {
            println("Found 3 at index $i")
        }
    }
}
```

### Pattern : Null Safety Safe Calls
 `?.` trả về `null` nếu đối tượng null thay vì ném ngoại lệ (Crash).

**Code Demo:**

```kotlin
fun printLength(str: String?) {
    // Safe Call Operator (?.)
    // Nếu str là null, in ra "null".
    // Nếu str có giá trị, in ra độ dài.
    println(str?.length) 
}
```

## SECTION 5: ANTI-PATTERNS & WARNINGS


3.  **Quên xử lý Null với `!!` (Bang operator):**
    *   **Tại sao nguy hiểm:** `value!!` ép buộc Kotlin tin rằng biến không null. Nếu giá trị thực sự là `null`, app sẽ **Crash** ngay lập tức. Chỉ dùng khi bạn chắc chắn 100% giá trị không bao giờ null.

fun printLength(text: String?) {
    val length = text!!.length
    println(length)
}

fun main() {
    printLength(null)
} //Exception in thread "main" kotlin.KotlinNullPointerException
text có kiểu String? → có thể là null

text!! nói với Kotlin rằng: “Tin tôi đi, nó không null”

Nhưng thực tế truyền vào null → Crash ngay lập tức

## SECTION 6: MASTER CHEAT SHEET

### Quick Reference Rules

*   **Biến:** `val` là vua. Chỉ dùng `var` khi giá trị phải đổi.
*   **Kiểu dữ liệu:** Để Kotlin tự suy diễn (`val x = 10`), chỉ khai báo khi cần thiết (`val x: Int`).
*   **String:** Dùng `""` (dấu ngoặc kép kép) cho `"$variable"` để chèn biến dễ dàng.
*   **Null:** `.` để truy cập thường gây lỗi nếu null. Dùng `?.` để an toàn. Dùng `?:` để gán giá trị mặc định nếu null.

### Decision Logic (If-Else Style)

*   **Nếu** cần lưu trữ 1 giá trị vĩnh viễn? → Dùng `val`.
*   **Nếu** cần danh sách thay đổi kích thước? → Dùng `MutableList`.
*   **Nếu** cần danh sách truy cập nhanh theo index? → Dùng `Array`.
*   **Nếu** cần kiểm tra nhiều điều kiện? → Dùng `When`.
*   **Nếu** biến có thể null? → Dùng `Type?` và xử lý bằng `?.` hoặc `?:`.

### Pattern 2: Overflow-Safe Large Numbers
**Khi nào dùng**: When dealing with IDs, timestamps, or counts that exceed 2 billion.
**Tại sao đúng**: Using `Long` prevents overflow errors.

```kotlin
// Standard Int: Max 2,147,483,647
val userId: Int = 1_000_000_000
val nextId: Int = userId + 1_000_000_000 // Overflow: Becomes negative!

// Safe Long: Max 9,223,372,036,854,775,807
val safeUserId: Long = 1_000_000_000L // Note the 'L' suffix
val nextSafeId: Long = safeUserId + 1_000_000_000L // Result: 2,000,000,000 (Correct)
```

### Pattern 3: Readable Magic Numbers
```kotlin
// Hard to read
val cacheSize = 1048576
val accountBalance = 5000000000

// Easy to read
val cacheSize = 1_048_576
val accountBalance = 5_000_000_000
val networkPacket = 0b11010010_01101001 // Binary split
```

### Pattern 4: Explicit Type Casting
```kotlin
val temperatureCelsius: Int = 25

// Compile Error: Type mismatch
// val byteTemp: Byte = temperatureCelsius 

// Explicit casting (Safe if value fits in Byte range -128 to 127)
val byteTemp: Byte = temperatureCelsius.toByte()
```

**String (Chuỗi ký tự)**
- Chuỗi là chuỗi các ký tự được đặt trong dấu nháy kép (`""`).
- Hỗ trợ các ký tự đặc biệt (escape characters) như `\n`.
- **Raw String (Chuỗi thô)**: Dùng `"""` để chứa văn bản đa dòng, bỏ qua các ký tự escape.


**String Template (Mẫu chuỗi)**
Cách chèn biến hoặc biểu thức trực tiếp vào chuỗi mà không cần nối chuỗi thủ công (`+`).
- Dấu `$` để chèn biến.
- Dấu `${}` để chèn biểu thức phức tạp.

```kotlin
val balance = 1000
val fee = 50
// Chèn biến
val msg1 = "Số dư: $balance"
// Chèn biểu thức
val msg2 = "Tổng tiền phải trả: ${balance + fee}"
```

---


### Pattern 1: The "Safe Initialization" Pattern (Using `val`)

**Tại sao đúng:**
Tuân thủ nguyên lý immutability. Tránh việc vô tình sửa đổi giá trị gốc gây lỗi logic.

```kotlin
class User {
    // Luôn dùng val cho ID hoặc dữ liệu cố định
    val id: Int = 1
    var username: String = ""

    fun updateName(newName: String) {
        // Không sửa id, chỉ sửa username (var)
        username = newName
    }
}
```

### Pattern 2: String Formatting for Logs/Messages

**Khi nào dùng:**
Khi cần tạo log message, thông báo UI hoặc query database có chứa nhiều tham số biến.

**Tại sao đúng:**
Dễ đọc, dễ maintain, không lo lỗi thứ tự tham số như kiểu `printf`.

```kotlin
fun generateOrderMessage(items: Int, total: Double): String {
    val header = "Don Hang Moi"
    
    // Dùng template expression ${} cho logic hoặc format phức tạp
    return """
        $header
        So luong: $items
        Thanh tien: $total VND
        Giam gia: ${if (items > 10) "Co" else "Khong"}
    """.trimIndent() // .trimIndent() xóa khoảng trắng thừa ở đầu dòng
}
```

---

## SECTION 5: ANTI-PATTERNS & WARNINGS

### 2. String Concatenation Hell (`+` quá nhiều)
- **Lý do nguy hiểm:** Code `s1 + s2 + s3` tạo ra nhiều object String rác (garbage) gây tốn bộ nhớ, và rất khó đọc khi có nhiều biến.
- **Khắc phục:** Dùng **String Template** (`$` và `${}`) hoặc nếu loop nối chuỗi thì dùng `StringBuilder`.

### 3. Quên Escape Characters trong String thường
- **Lý do nguy hiểm:** Dùng `"` trong chuỗi `"` làm gãy chuỗi, gây lỗi biên dịch.
- **Khắc phục:** Dùng **Raw String** (`"""`) nếu chuỗi chứa nhiều dấu nháy kép hoặc định dạng phức tạp.

---

## SECTION 2: DECISION TABLES

### Table 2: For Loop vs While Loop (Vòng lặp)
| Tình huống sử dụng | Nên dùng gì | Tại sao - EN + VI | Sai lầm thường gặp |
|--------------------|-------------|-------------------|---------------------|
| Lặp qua collection/array | `for (item in collection)` | **Iterator Safety**: Tự động xử lý iterator, tránh lỗi `IndexOutOfBoundsException` | Dùng `while` với index thủ công → dễ tràn index, code dài |
| Lặp có步长 (step) hoặc range | `for (i in 1..100 step 2)` | **Built-in Range Support**: `downTo`, `step` là keywords, không cần tính toán | Tính `i += 2` trong `while` → dễ sai logic, không handle negative range |
| Lặp vô tận hoặc điều kiện phức tạp | `while (condition) { }` hoặc `do { } while` | **Conditional Execution**: Duyệt khi điều kiện thay đổi runtime, không xác định trước số lần | Dùng `for` với vô hạn → compile error hoặc infinite loop không break |
| Cần index + element | `for ((idx, elem) in collection.withIndex())` | **Destructuring**: Truy cập đồng thời index và element, không cần map thủ công | Lặp 2 lần: lần 1 get index, lần 2 get element → inefficiency |

---

## SECTION 4: CODE PATTERNS

### Pattern 1: Range Validation with When
**Khi nào dùng**: Kiểm tra input người dùng (tuổi, số lượng, score) có trong phạm vi hợp lệ.
**Tại sao đúng**: Dùng `in` + `when` để validate rõ ràng, return value trực tiếp.

```kotlin
fun validateAge(age: Int): String {
    return when {
        age < 0 -> "Tuổi không hợp lệ"
        age in 0..17 -> "Người chưa đủ tuổi"
        age in 18..65 -> "Người lao động"
        age > 65 -> "Người cao tuổi"
    }
}

// Usage
val result = validateAge(25) // "Người lao động"
```

### Pattern 2: For Loop with Destructuring
**Khi nào dùng**: Duyệt qua `Map` hoặc `List` cần cả key và value/index.
**Tại sao đúng**: `withIndex()` + destructuring = một dòng code, không cần biến phụ.

```kotlin
val tasks = listOf("Code", "Test", "Deploy")

for ((index, task) in tasks.withIndex()) {
    println("Công việc $index: $task")
}
```


### Pattern 4: When with Type Check
**Khi nào dùng**: Xử lý polymorphic input (JSON, Message, Event).
**Tại sao đúng**: `is` keyword auto smart cast, không cần manual cast.

```kotlin
fun processInput(input: Any) {
    when (input) {
        is String -> println("Chuỗi có độ dài ${input.length}")
        is Int -> println("Số nguyên: ${input * 2}")
        is List<*> -> println("List có ${input.size} phần tử")
        else -> println("Kiểu không xác định")
    }
}
```

---





## Kotlin Collections – Quick Notes

- **`listOf()`**  
  Dùng cho danh sách **cố định** (menu, tag, constant).  
  **Immutability**: bất biến, chỉ đọc → an toàn, tối ưu đọc.  
  ❌ Không thể `.add()` / `.remove()`.

- **`mutableListOf()`**  
  Dùng khi cần **thêm/xóa** phần tử sau khi khởi tạo.  
  **Mutability**: cho phép thay đổi nội dung list.  
  ⚠️ Dễ nhầm giữa *mutation* (add/remove) và *reassignment*.

- **`intArrayOf()` / `arrayOf()`**  
  Dùng cho collection **size cố định**, ưu tiên hiệu năng (primitive).  
  **Performance**: tránh boxing overhead.  
  ❌ Không thể thay đổi kích thước mảng, chỉ gán theo index.

- **`arrayOf()` / `List`**  
  Dùng khi **không biết trước size** hoặc cần **mixed types**.  
  **Flexibility**: linh hoạt về kiểu dữ liệu.  
  ⚠️ Không phù hợp cho vòng lặp hiệu năng cao (casting, overhead).

### Data Flow

---
## SECTION 4: CODE PATTERNS (READY TO USE)

### Pattern 1: The Read-Only Pipeline
**Khi nào dùng**: When you have data that shouldn't change once defined (configuration, constants).
**Tại sao đúng**: Enforces data integrity and prevents side effects.

```kotlin
fun main() {
    // 1. Define using val + listOf for safety
    val tools = listOf("Hammer", "Wrench", "Screwdriver")

    // 2. Iterate safely (Standard For-Loop)
    for (tool in tools) {
        println("Tool: $tool")
    }

    // 3. Access by index
    val firstTool = tools[0] // "Hammer"
}
```

### Pattern 2: The Dynamic Builder
**Khi nào dùng**: When processing input or accumulating results (e.g., collecting API responses).
**Tại sao đúng**: `mutableListOf` allows the collection to grow/shrink as data arrives.

```kotlin
fun main() {
    // 1. Initialize empty mutable list
    val userInputs = mutableListOf<String>()

    // 2. Add items dynamically
    userInputs.add("First")
    userInputs.add("Second")
    
    // 3. Remove item (Boolean return)
    val wasRemoved = userInputs.remove("First") 

    println(userInputs) // Output: [Second]
}
```

### Pattern 3: Primitive Arrays for Performance
**Khi nào dùng**: When dealing with large amounts of numbers (integers, doubles) where memory matters.
**Tại sao đúng**: `intArrayOf` stores primitives directly, avoiding the overhead of `List<Int>`.

```kotlin
fun main() {
    // 1. Specific type array
    val scores = intArrayOf(10, 20, 30)

    // 2. Combining arrays
    val newScores = intArrayOf(40, 50)
    val allScores = scores + newScores // [10, 20, 30, 40, 50]

    // 3. Modifying in place
    scores[0] = 100 
}
```
---
## SECTION 6: MASTER CHEAT SHEET
### Quick Reference Rules
- **`listOf()`**: Read-only. Use for constants.
- **`mutableListOf()`**: Read/Write. Use for dynamic data.
- **`arrayOf()`**: Fixed size. Use for primitives or specific Java interop.
- **`val`**: Cannot reassign the variable.
- **`var`**: Can reassign the variable.
- **Rule of thumb**: If `val` + `mutableListOf()`, you can change contents but not the list object itself.

## SECTION 2: DECISION TABLES

### Table 1: Handling Null Variables
| Tình huống sử dụng | Nên dùng gì | Tại sao - Safe Call Operator (`?.`) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Truy cập thuộc tính của object có thể null (VD: `user?.name`) | **`?.`** | **Safe Call**: Nếu object null, dòng code bỏ qua việc truy cập thay vì crash. Trả về `null` nếu object null. | Dùng `.` thay cho `?.`导致 crash. |
| Cần trả về giá trị mặc định nếu null (VD: `count ?: 0`) | **`?:`** | **Elvis Operator**: Cung cấp giá trị fallback (mặc định) ngay lập tức nếu biến null. | Viết dài dòng: `if (count != null) count else 0`. |
| Buộc biến không null (khi bạn chắc chắn 100%) (VD: `val len = s!!.length`) | **`!!`** | **Non-null Assertion**: Dùng khi logic code đảm bảo biến không null, hoặc bạn đang build prototype. | Lạm dụng `!!` trong code production, dễ gây crash nếu logic sai. |

### Table 2: Variables Declaration
| Tình huống sử dụng | Nên dùng gì | Tại sao - Nullable Type (`?`) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Biến nhận dữ liệu từ API hoặc User Input | **`Type?`** | **Safety**: Dữ liệu đầu vào không bao giờ an toàn tuyệt đối. Khai báo nullable bắt buộc phải xử lý. | Khai báo `Type` (non-null) nhưng gán `null` được (Compiler error). |
| Biến khởi tạo ngay và không bao giờ thay đổi thành null | **`val: Type`** | **Guarantee**: Compiler đảm bảo biến luôn có giá trị, bạn không cần kiểm tra null mỗi khi dùng. | Khai báo `var` (mutable) khi không cần thiết, làm code phức tạp. |

---
