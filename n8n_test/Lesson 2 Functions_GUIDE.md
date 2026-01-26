# DEVELOPER DECISION GUIDE: Lesson 2 Functions.pdf
## SECTION 3: ARCHITECTURE & RELATIONSHIPS
### Hierarchy of Execution
```text
[Program Process]
       |
       v
[main(args: Array<String>)] <--- Entry Point
       |
       +---> (Arguments Parser)
       |
       v
[Function Calls] <--- Custom Logic
       |
       v
[Output / Return Value]
```

### Data Flow
1. **Input**: JVM / User passes arguments.
2. **Storage**: `args` is an `Array<String>`.
3. **Processing**: `main` calls other functions.
4. **Output**: `println()` writes to console.

## SECTION 4: CODE PATTERNS

### Pattern 1: The Basic Entry Point
**When to use (Khi nào dùng)**: Luôn luôn cho mọi file Kotlin executable.
**Why this pattern is correct**: Cú pháp chuẩn, tối thiểu, chuẩn bị environment cho JVM.
```kotlin
// File: Main.kt
fun main() {
    println("Program started.")
}
```

### Pattern 2: Entry Point with Arguments
**When to use (Khi nào dùng)**: Khi cần thay đổi hành vi program mà không recompile code.
**Why this pattern is correct**: `Array<String>` lưu trữ biến runtime. `${}` giúp formatting an toàn.
```kotlin
fun main(args: Array<String>) {
    if (args.isNotEmpty()) {
        val name = args[0]
        println("Hello, $name")
    } else {
        println("Hello, stranger")
    }
}
```

### Pattern 3: Standard Function (Reusability)
**When to use (Khi nào dùng)**: Khi logic phức tạp hoặc cần dùng lại ở nhiều nơi.
**Why this pattern is correct**: Tách biệt logic, `Unit` return type mặc định, clean code.
```kotlin
fun printUserScore(username: String, score: Int) {
    println("$username has $score points")
}

fun main() {
    printUserScore("Dev1", 100)
}
```
## SECTION 1: CORE MENTAL MODEL
### Core Concepts (Tư duy cốt lõi)
**1. Everything is an Expression (Mọi thứ là biểu thức)**
- Hầu hết mọi thứ trong Kotlin trả về giá trị, kể cả `if/else`.
- Kết quả của một khối mã là giá trị của biểu thức cuối cùng.

```kotlin

// Kotlin: Gọn gàng, là biểu thức (Expression)
val temperature = 20
val isHot = if (temperature > 40) true else false 
```

**2. Unit Type (Đơn vị)**
- Tương đương `void` trong Java, nhưng là một **Object**.
- Nếu hàm không return gì, Kotlin mặc định trả về `Unit`.
- `Unit` là singleton (chỉ có 1 instance duy nhất).

```kotlin
// 2 cách này equivalent (tương đương)
fun logMessage(msg: String) {
    println(msg) // Return type Unit là mặc định
}
```
---
## SECTION 2: DECISION TABLES
### Table 2: Parameters & Arguments

| Tình huống sử dụng | Nên dùng gì | Tại sao (Why) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Parameter có giá trị mặc định, gọi hàm linh hoạt | Dùng **Default Parameters** (`name: String = "default"`) | **Flexibility**: Giảm số lượng overload hàm (hàm cùng tên, tham số khác nhau). | Viết nhiều hàm重载 (overload) thay vì dùng default value. |
| Gọi hàm có nhiều tham số, khó nhớ thứ tự | Dùng **Named Arguments** (`func(a = 1, b = 2)`) | **Readability**: Rõ ràng tham số nào đang được gán giá trị gì. | Bỏ qua named arguments khi tham số nhiều -> Dễ bị nhầm thứ tự. |

---

## SECTION 3: ARCHITECTURE & RELATIONSHIPS

### Parameter Hierarchy (Xử lý tham số)
1. **Named Arguments**: Ưu tiên cao nhất khi gọi.
2. **Default Values**: Khi tham số bị bỏ trống.
3. **Positional Arguments**: Nếu không dùng named.

---

## SECTION 4: CODE PATTERNS (READY TO USE)

### Pattern 1: The Expression Function (Hàm biểu thức)
**Khi nào dùng**: Khi logic ngắn gọn, chỉ cần return một giá trị đơn giản.
**Tại sao đúng**: Loại bỏ `return` keyword rườm rà, tăng độ đọc.

```kotlin
// Pattern: Body là một biểu thức
fun calculateArea(width: Int, height: Int) = width * height

// Sử dụng
val area = calculateArea(10, 20) // area = 200
```

### Pattern 2: Flexible API with Default Params (API linh hoạt)
**Khi nào dùng**: Xây dựng hàm utility hoặc hàm config cho library.
**Tại sao đúng**:backward compatibility tốt. Người dùng cũ không cần sửa code khi thêm tham số mới.

```kotlin
// Pattern: Parameter với default value
fun createNotification(
    message: String, 
    title: String = "Alert", 
    isUrgent: Boolean = false
) {
    println("[$title] $message (Urgent: $isUrgent)")
}

// Sử dụng linh động
createNotification("Chập chờn điện") 
// Output: [Alert] Chập chờn điện (Urgent: false)

createNotification("Sập nguồn", "CRITICAL", true)
// Output: [CRITICAL] Sập nguồn (Urgent: true)
```
---

## SECTION 6: MASTER CHEAT SHEET

### Quick Reference Rules (Quy tắc nhanh)

1. **Expression Rule**: `if`, `when`, `try/catch` đều là expressions. Dùng để gán giá trị.
2. **Unit Rule**: Hàm không return = `Unit`. Không cần khai báo显式.
3. **Default Rule**: Dùng `param: Type = value` thay vì viết nhiều hàm.
4. **Call Rule**: Dùng `name = value` khi tham số > 2 hoặc dễ nhầm lẫn.


**First-Class Function (Hàm cấp 1)**
Khả năng của hàm trong Kotlin được treated như một biến dữ liệu thông thường (lưu trữ, truyền làm tham số, trả về).

```kotlin
// 1. Lưu trữ trong biến
val filter: (Int) -> Int = { level -> level / 2 }

// 2. Trả về từ hàm khác
fun getMultiplier(factor: Int): (Int) -> Int {
    return { x -> x * factor }
}

// 3. Truyền làm tham số
fun calculate(a: Int, b: Int, op: (Int, Int) -> Int): Int = op(a, b)
```

**Single-Expression Function (Hàm biểu thức đơn)**
Shortcut để return giá trị trực tiếp mà không cần khối `{} và return`. Giảm boilerplate cho logic đơn dòng.

```kotlin
// Tránh: Khối thừa cho logic đơn giản
fun squareOld(x: Int): Int {
    return x * x
}

// Nên: Gọn, rõ ràng
fun square(x: Int): Int = x * x
```

**Argument Passing Strategy (Chiến lược truyền đối số)**
Kotlin ưu tiên **Named Arguments** để tránh nhầm lẫn thứ tự tham số, đặc biệt khi hàm có nhiều tham số hoặc có tham số mặc định.

---

## SECTION 2: DECISION TABLES

### Table 1: Positional vs Named Arguments

| Tình huống sử dụng | Nên dùng gì | Tại sao - EN term + VI explanation | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Hàm có 1-2 tham số đơn giản | **Positional Arguments** | Trực quan, ngắn gọn. Caller không cần gõ tên biến. | Lạm dụng tên biến cho hàm `max(a, b)`. |
| Hàm > 2 tham số hoặc có tham số mặc định | **Named Arguments** | **Readability** (Đọc được). Tránh sai thứ tự, bỏ qua tham số mặc định không cần thiết. | Bỏ qua tên biến → Crash hoặc logic sai do truyền sai thứ tự. |
| Khi refactoring hàm cũ | **Named Arguments** | **Safety** (An toàn). Dù hàm thay đổi thứ tự tham số, code gọi vẫn đúng. | Sửa hàm xong, code gọi bị sai logic im lìm. |

### Table 2: Standard Function vs Lambda vs Single-Expression

| Tình huống sử dụng | Nên dùng gì | Tại sao - EN term + VI explanation | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| Logic phức tạp, nhiều dòng code | **Standard Function** (`fun name() { ... }`) | Dễ debug, tách biệt logic rõ ràng. | Ép vào lambda quá dài, khó đọc. |
| Logic ngắn gọn, trả về ngay, cần truyền vào hàm khác | **Lambda** (`{ ... }`) | **Conciseness** (Ngắn gọn). Rất phù hợp với collection operations (filter, map). | Viết lambda quá dài, không có return type rõ ràng. |
| Logic chỉ là 1 biểu toán hoặc 1 hàm đơn giản | **Single-Expression** (`fun name() = ...`) | **Readability** (Đọc được). Loại bỏ boilerplate `return`. | Quên `=` khi cần return, hoặc dùng `fun name() { ... }` thừa. |

---

## SECTION 3: ARCHITECTURE & RELATIONSHIPS

### Logic Hierarchy of Function Definitions

```text
[ Function Definition ]
       |
       +-- [ Signature ]
       |     |-- Name
       |     |-- Parameters (Input)
       |     |-- Return Type (Output)
       |
       +-- [ Body ]
             |-- Standard Block: { ... }
             |     |-- Complex Logic
             |     |-- Multiple Statements
             |
             |-- Single Expression: = ...
                   |-- Simple Calculation
                   |-- Direct Return
```

### Data Flow: Higher-Order Function

```text
[ Caller Code ]
      |
      v
[ Higher-Order Function ] (e.g., encodeMsg)
      | Receives: Data (String) + Logic (Function)
      | Action: Wraps Data with Logic
      v
[ Lambda / Function Reference ]
      | Executes specific operation
      v
[ Result ]
```

---

## SECTION 4: CODE PATTERNS (READY TO USE)

### Pattern 1: Safe Function with Defaults & Named Args

**Khi nào dùng:** Khi thiết kế API hoặc utility functions có nhiều option, muốn giữ backward compatibility và dễ đọc.

**Tại sao đúng:** Giúp caller chỉ cần truyền dữ liệu bắt buộc, tự động dùng setting mặc định an toàn mà không cần nhớ thứ tự.

**Code Demo Hoàn Chỉnh:**

```kotlin
// Definition
fun reformat(
    str: String,
    wordSeparator: Char = '_',
    normalizeCase: Boolean = true,
    divideByCamelHumps: Boolean = false
) {
    var result = str
    if (normalizeCase) result = result.lowercase()
    if (divideByCamelHumps) {
        // Logic tách camel case
        result = result.replace(Regex("([a-z])([A-Z])"), "$1$wordSeparator$2")
    }
    println("Result: $result")
}

// Usage
fun main() {
    // Case 1: Gọi cơ bản (dùng mặc định)
    reformat("HelloWorld") 
    
    // Case 2: Đặt tên rõ ràng cho tham số tùy chọn
    reformat(
        str = "HelloWorld", 
        divideByCamelHumps = true, 
        wordSeparator = '-'
    )
}
```

### Pattern 2: Lambda as Parameter (Higher-Order)

```kotlin
// Definition
fun processSensorData(
    rawData: Int, 
    sensorType: String, 
    validator: (Int, String) -> Boolean
): String {
    return if (validator(rawData, sensorType)) {
        "Valid data: $rawData"
    } else {
        "Invalid data"
    }
}

// Usage
fun main() {
    // Logic nghiệp vụ được truyền vào dưới dạng Lambda
    val isSafe = processSensorData(100, "Temp") { value, type ->
        value < 120 && type == "Temp"
    }
    
    // Logic khác cho cùng hàm khung
    val isPressureSafe = processSensorData(900, "Pressure") { value, _ ->
        value in 800..1000
    }
}
```

### Pattern 3: Function Type Variable

**Khi nào dùng:** Khi cần lưu trữ logic vào danh sách hoặc biến để gọi động sau này.

**Tại sao đúng:** Biến hàm là dữ liệu, có thể di chuyển và sử dụng linh hoạt.

**Code Demo Hoàn Chỉnh:**

```kotlin
fun main() {
    // Khai báo biến持有 hàm
    val waterFilter: (Int) -> Int = { level -> level / 2 }
    val airFilter: (Int) -> Int = { level -> level - 10 }

    // Lưu vào List
    val filters = listOf(waterFilter, airFilter)

    // Gọi động
    val dirtLevel = 20
    filters.forEach { filter ->
        println("Filtered level: ${filter(dirtLevel)}")
    }
}
```

---

## SECTION 5: ANTI-PATTERNS & WARNINGS

2.  **Optional Parameters Before Required Parameters**
    *   **Danger:** Violates logic đọc code. Caller bắt buộc phải pass arguments cho các parameter đầu tiên dù nó là optional.
    *   **Code Sai:**
        ```kotlin
        fun log(tag: String = "App", msg: String) // Lỗi: Msg không thể omit được nếu không dùng tên biến
        ```
    *   **Solution:** Luôn để tham số bắt buộc (Required) trước, tham số mặc định (Default) sau.

3.  **Returning Null from Single-Expression Functions**
    *   **Danger:** Dùng `=` cho single-expression nhưng `if` return `null` trong khi function type không nullable.
    *   **Code Sai:**
        ```kotlin
        fun check(x: Int): Int = if (x > 0) x else null // Compiler Error hoặc Runtime Error
        ```
---
# DEVELOPER DECISION GUIDE: Higher-Order Functions & Collections
### Core Definitions
*   **Higher-Order Function (HOF - Hàm bậc cao):** A function that accepts another function as a parameter or returns a function. Used to abstract behavior.
*   **Function Type (Loại hàm):** Defines the signature of a function variable (e.g., `(String) -> String`).
*   **Lambda (Hàm ẩn danh):** An anonymous function passed inline. Defined by curly braces `{}`.
*   **Function Reference (Tham chiếu hàm):** Using `::` to pass a named function as an argument.
*   **Last Parameter Call Syntax (Kỹ thuật gọi tham số cuối):** Allows moving a lambda argument outside the parentheses `()`.

### Key Mental Model
Think of functions as "behavior variables." Instead of writing specific logic inside a function (hardcoded), you pass the *logic* itself as an argument. This makes your API generic.
---

## SECTION 2: DECISION TABLES

| Use Case (Tình huống sử dụng) | Nên dùng gì | Tại sao (Why) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| **Logic is used ONCE only.** | **Lambda (inline)** | **Conciseness:** Keeps logic visible right where it's called. No need to jump to another function definition. | Defining a named function when it's only called once (clutters namespace). |
| **Logic is used MULTIPLE times.** | **Function Reference (`::`)** | **Reusability:** Follows DRY (Don't Repeat Yourself) principle. Easier to unit test. | Copy-pasting the same lambda block in 3 different places. |
| **Iterating a List with 1 parameter.** | **Implicit `it`** | **Readability:** Reduces boilerplate. Standard Kotlin idiomatic style. | Writing `{ x -> x > 0 }` instead of `{ it > 0 }`. |
| **Filtering large datasets.** | **Sequence (Lazy)** | **Performance:** Prevents creating intermediate collections in memory. Evaluation stops early if possible. | Using `List.filter().filter()` on massive lists instead of `asSequence()`. |
| **Simple iteration (void return).** | **`repeat()` / `forEach()`** | **Clarity:** Explicit intent to iterate without managing indices (`for` loops). | Using a `for (i in 0..10)` loop when `repeat(10) { ... }` is cleaner. |

---

## SECTION 3: ARCHITECTURE & RELATIONSHIPS

### Execution Flow
This diagram shows how a HOF accepts a function type argument. The **Implementation** (Lambda/Ref) is injected into the **HOF** to be executed.

```text
[ Caller ]
    |
    | 1. Calls
    v
[ Higher-Order Function (HOF) ]
    | Logic Structure (e.g., Loop, Connect, Validate)
    |
    | 2. Injects & Executes
    +-------------------------> [ Function Argument ]
                                    (The "Behavior")
                                        |
                                        | 3. Runs specific logic
                                        v
                                    [ Result / Side Effect ]
```

### Syntax Variations
*   **Standard:** `encodeMsg("abc", { it.toUpperCase() })`
*   **Last Param Syntax (Trailing):** `encodeMsg("abc") { it.toUpperCase() }`
*   **Function Reference:** `encodeMsg("abc", ::enc2)`

---

### Pattern 1: The Standard Filter
**When to use:** You need to extract a subset of a list based on a condition.

```kotlin
fun main() {
    val colors = listOf("red", "green", "blue", "red-orange")
    
    // Pattern: collection.filter { condition }
    val reds = colors.filter { color ->
        color.contains("red")
    }
    
    println(reds) // [red, red-orange]
}
```

### Pattern 2: Implicit "it" Iteration
**When to use:** The lambda takes exactly one parameter and you want to minimize code noise.

```kotlin
fun main() {
    val numbers = listOf(1, -5, 3, -2)
    
    // Explicit
    val positivesExplicit = numbers.filter { num -> num > 0 }
    
    // Implicit (Preferred in Kotlin)
    val positivesImplicit = numbers.filter { it > 0 }
    
    println(positivesImplicit) // [1, 3]
}
```

### Pattern 3: Function Reference Injection
**When to use:** You have a pre-existing, named function that matches the signature required by the HOF.

```kotlin
// Common in Android: Activity callbacks or Network handlers
fun main() {
    val inputs = listOf("cmd1", "cmd2")
    
    // Execute each string using a named function
    inputs.forEach(::executeCommand)
}

fun executeCommand(cmd: String) {
    println("Executing: $cmd")
}


---
## SECTION 6: MASTER CHEAT SHEET

### Top 10 Rules
1.  **HOF:** Function taking a function.
2.  **Syntax:** Put Lambda **inside** `{ }`.
3.  **Trailing Lambda:** If it's the last arg, move it **outside** `( )`.
4.  **One Param:** Use `it`. Don't write `{ x -> x }`.
5.  **Named Function:** Use `::` reference.
6.  **Filter:** Returns a NEW list containing items where {it} is `true`.
7.  **Iteration:** `forEach { }` iterates, `filter { }` selects.
8.  **Performance:** Use `.asSequence()` for large data chains.
9.  **Types:** Know `(Int) -> Unit` syntax.
10. **Clean Code:** Don't define a named function if you only use it once.

### Decision Logic (If-Else)
*   **IF** the logic is simple and used once -> **Lambda inline**.
*   **IF** the logic is complex or reused -> **Named Function + `::` reference**.
*   **IF** the list is huge (>10k items) -> **Use Sequence**.
*   **IF** the parameter is a lambda and last -> **Trailing syntax**.
# DEVELOPER DECISION GUIDE: Lesson 2 Functions
**Sequence (Chuỗi lười biếng)**: Dòng dữ liệu chỉ xử lý phần tử khi cần thiết. Thay vì tạo collection mới ngay lập tức, nó tạo ra một "kế hoạch" thực thi.
**Eager (Nhiệt tình)**: Xử lý ngay lập tức, tạo ra collection mới ở mỗi bước.

**Why is Sequence better?**
- Khi xử lý large datasets hoặc nhiều bước transform (filter -> map -> filter), Sequence tránh được việc tạo ra nhiều intermediate collections, tiết kiệm bộ nhớ và CPU.

```kotlin
// Eager: Tạo 2 list trung gian ([1,2,3] -> [2,4,6] -> [2,4])
val eager = listOf(1, 2, 3, 4, 5)
    .filter { it % 2 == 0 }      // List [2,4]
    .map { it * 2 }              // List [4,8]

// Sequence: Chạy từng phần tử qua hết các bước
val lazy = listOf(1, 2, 3, 4, 5)
    .asSequence()                // Chuyển sang chế độ lười
    .filter { it % 2 == 0 }      // Chưa làm gì cả
    .map { it * 2 }              // Chưa làm gì cả
    .toList()                    // Tại đây mới xử lý: 2 -> 4 -> 4 -> 8
```

## SECTION 2: DECISION TABLES

### Table 1: Collection Operations

| Tình huống sử dụng | Nên dùng gì | Tại sao - Lazy Evaluation (Đánh giá lười biếng) | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| **Datasets nhỏ (< 1000 phần tử)** | Collection Operations (List/Set) | Overhead của Sequence creation > Performance gain. Nhanh hơn do không phải chuyển đổi state. | Dùng Sequence cho list 10 phần tử, gây chậm máy không cần thiết. |
| **Datasets lớn / Nhiều bước transform** | Sequence | Tránh tạo intermediate collections. Dừng processing ngay khi tìm thấy kết quả (terminal op). | Dùng Collection với `map` -> `filter` -> `map` lồng nhau, tạo rác bộ nhớ (GC pressure). |
| **Cần build UI (Android Adapter)** | Collection | UI render cần list rõ ràng. `asSequence().toList()` là rác. | Dùng Sequence trực tiếp trong `RecyclerView.Adapter` (nếu không convert về List). |

### Table 2: Transformations

| Tình huống sử dụng | Nên dùng gì | Tại sao | Sai lầm thường gặp |
| :--- | :--- | :--- | :--- |
| **Nhân đôi giá trị (Element-wise)** | `map { it * 2 }` | Duyệt qua từng phần tử và apply transform. | Dùng `forEach` và thêm vào mutable list mới (lằng nhằng, dễ lỗi). |
| **Làm phẳng list con (Nested List)** | `flatten()` | Trả về một list duy nhất chứa mọi phần tử. | Dùng `flatMap` với logic trả về list rỗng thay vì `flatten()` cho cấu trúc đơn giản. |

## SECTION 4: CODE PATTERNS (READY TO USE)

### Pattern 1: Lazy Filtering Chain
**Khi nào dùng**: Khi bạn có nhiều bước lọc/xử lý và chỉ cần kết quả cuối cùng.
**Tại sao đúng**: Giảm số lần tạo đối tượng trung gian, tối ưu CPU.

```kotlin
fun processHeavyData(items: List<String>): List<String> {
    return items.asSequence()
        .filter { it.startsWith("A") }    // Bước 1: Lọc
        .map { it.uppercase() }           // Bước 2: Chuyển đổi
        .filter { it.length > 3 }         // Bước 3: Lọc lại
        .take(10)                         // Bước 4: Giới hạn
        .toList()                         // Thực thi & Trả về List
}
```

### Pattern 2: Safe Data Transformation (Set -> List)
**Khi nào dùng**: Khi input là Set (không trùng lặp) nhưng output cần List hoặc xử lý thêm.
**Tại sao đúng**: `flatten()` xử lý cấu trúc nested dễ dàng, `map` thay đổi giá trị chuẩn xác.

```kotlin
val nestedSets = listOf(setOf(1, 2, 3), setOf(4, 5), setOf(1, 2))

// Mục đích: Lấy tất cả số, loại bỏ duplicate, nhân đôi
val result = nestedSets
    .flatten()                 // [1,2,3,4,5,1,2]
    .toSet()                   // Đảm bảo duy nhất: {1,2,3,4,5}
    .map { it * 2 }            // [2,4,6,8,10]
    .sorted()                  // Sắp xếp
```
## SECTION 5: ANTI-PATTERNS & WARNINGS
2.  **Dùng `forEach` thay cho `map`**
    *   **Code Sai**:
        ```kotlin
        val bad = mutableListOf<Int>()
        list.forEach { bad.add(it * 2) } // Side effect, khó đọc
        ```
    *   **Why Bad**: Khó maintain, không khai báo biến mutable nếu không cần thiết. Dùng `map` để trả về giá trị mới trực tiếp.

3.  **Tạo Sequence cho List < 1000 phần tử**
    *   **Why Bad**: Chi phí tạo đối tượng `Sequence` và truy cập qua `Iterator` tốn kém hơn List index access trực tiếp.

## SECTION 6: MASTER CHEAT SHEET

**Top 5 Rules:**
1.  **Eager là mặc định**: List, Set xử lý ngay.
2.  **Lazy là Sequence**: Dùng `.asSequence()` ở đầu pipeline.
3.  **Terminal Operation**: Phải có `toList()`, `sum()`, `find()`, `count()` để kích hoạt Sequence.
4.  **`map`**: Transform 1-1.
5.  **`flatten()`**: Mở nested list.

**Logic Decision (If-Else):**
*   **IF** Dataset < 1000 items?
    *   **THEN** Use `list.filter { }.map { }` (Eager)
*   **IF** Dataset > 1000 items OR complex chain (filter > map > filter)?
    *   **THEN** Use `asSequence().filter { }.map { }.toList()` (Lazy)
*   **IF** Input is List of Lists?
    *   **THEN** Use `flatten()` hoặc `flatMap`
