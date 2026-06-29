# RBL-4 - File Tổng Hợp Phân Công Nhóm

Đây là file điều phối chính cho cả nhóm.  
Tất cả thành viên nên đọc file này trước khi bắt đầu làm RBL-4.

## 1. Hướng nghiên cứu cố định

Nhóm phải bám đúng `proposal RBL-3` đã được duyệt.

- Đề tài: dùng `GPT-4o mini` như một quality gate để đánh giá bug report trên GitHub OSS
- Phạm vi đánh giá: `OB / EB / S2R`
- Metric chính: `Cohen's Kappa`
- Threshold chính: `Kappa >= 0.70`

## 2. Nguyên tắc chung cho cả nhóm

- Không tự đổi `RQ`, `metric`, `threshold`, hoặc `model`.
- Không tự sửa rubric nếu chưa thống nhất trong nhóm.
- Không tự đổi prompt nếu chưa ghi amendment rõ ràng.
- Phải làm `pilot` trước, ổn rồi mới chạy `full experiment`.
- Mọi output quan trọng đều phải lưu lại và đồng bộ về GitHub.

## 3. Các file chung mọi người phải biết

### File điều phối chính

- `README.md`
- `checklist.md`
- `notes.md`
- `rubric-ob-eb-s2r.md`
- `prompt_final.md`
- `pilot-workflow.md`
- `week8-full-experiment.md`
- `issue-handling-rules.md`
- `sync-results-to-github.md`

### File dữ liệu và kết quả mẫu

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`
- `results/pilot_llm_output.csv`
- `results/full_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_api_log.txt`
- `results/summary.csv`

## 4. Phân công theo từng thành viên

### Huy - PL (Project Lead)

**Vai trò chính:**

- Giữ thư mục master và bản cuối của tất cả file
- Kiểm tra 7 gate bắt buộc trước Tuần 7
- Chốt rubric cuối và prompt cuối
- Quyết định pilot đã đủ ổn để sang full experiment hay chưa
- Quyết định có cần amendment hay không
- Theo dõi deadline và gom output của cả nhóm

**Những file Huy cần theo sát nhất:**

- `checklist.md`
- `notes.md`
- `rubric-ob-eb-s2r.md`
- `prompt_final.md`
- `results/summary.csv`

**Việc cụ thể của Huy:**

1. Xác nhận cả nhóm chỉ bám proposal đã duyệt
2. Điền `notes.md` với ngày pilot, seed, size pilot, và quyết định cuối
3. Kiểm tra mọi người nộp file đúng format
4. Review kết quả pilot trước khi cho sang Tuần 8
5. Review output full experiment trước khi viết báo cáo cuối

### Hùng - DG (Data and Ground Truth)

**Vai trò chính:**

- Chuẩn bị pilot sample
- Chuẩn bị full dataset
- Gán nhãn dữ liệu
- Tạo consensus label của developer
- Kiểm tra IAA

**Những file Hùng phụ trách:**

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`

**Việc cụ thể của Hùng:**

#### Tuần 7 - Pilot

1. Chọn pilot sample từ:
   - `pandas`
   - `scikit-learn`
   - `VS Code`
2. Chọn ngẫu nhiên bằng random seed cố định
3. Ghi seed vào `notes.md`
4. Điền `data/pilot_sample.csv`
5. Gán nhãn toàn bộ pilot với vai trò annotator 1
6. Đảm bảo ít nhất 30% số dòng được double-label
7. Resolve disagreement và điền:
   - `consensus_ob`
   - `consensus_eb`
   - `consensus_s2r`
8. Báo IAA pilot lại cho Huy

#### Tuần 8 - Full experiment

1. Chuẩn bị full dataset
2. Điền `data/full_ground_truth.csv`
3. Đảm bảo có đủ phần double-label theo proposal
4. Tính IAA trên phần double-label của full set
5. Nếu IAA thấp hơn ngưỡng, phải dừng và báo Huy trước khi chạy LLM full

### Phúc - LR (LLM Runner)

**Vai trò chính:**

- Chuẩn bị pipeline gọi API
- Chạy GPT-4o mini trên pilot
- Chạy GPT-4o mini trên full dataset
- Lưu output và log cẩn thận

**Những file Phúc phụ trách:**

- `results/pilot_llm_output.csv`
- `results/full_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_api_log.txt`

**Việc cụ thể của Phúc:**

#### Tuần 7 - Pilot

1. Đảm bảo API test chạy được
2. Chỉ dùng prompt trong `prompt_final.md`
3. Chạy đúng cấu hình:
   - model = `GPT-4o mini`
   - temperature = `0.0`
4. Chạy trên `data/pilot_sample.csv`
5. Lưu output đã parse vào `results/pilot_llm_output.csv`
6. Lưu log từng call vào `results/pilot_api_log.txt`
7. Nếu response rỗng hoặc lỗi, đánh dấu `INVALID`, không tự điền nhãn

#### Tuần 8 - Full experiment

1. Chạy trên toàn bộ dataset đã duyệt với cùng config như pilot
2. Lưu output vào `results/full_llm_output.csv`
3. Lưu log vào `results/full_api_log.txt`
4. Nếu rate limit thì dùng retry với exponential backoff
5. Commit lên GitHub sau mỗi batch lớn để tránh mất dữ liệu
6. Nếu response format đổi bất thường, báo Huy ngay

### Thêm - MS (Metrics and Statistics)

**Vai trò chính:**

- Xác nhận script metric chạy được
- Tính toàn bộ metric ở pilot
- Tính toàn bộ metric ở full experiment
- Chuẩn bị bảng summary và diễn giải thống kê

**Những file Thêm phụ trách:**

- `results/pilot_analysis_plan.md`
- `results/summary.csv`
- `results/full_analysis.ipynb` nếu nhóm tạo file này

**Việc cụ thể của Thêm:**

#### Tuần 7 - Pilot

1. Confirm code metric chạy được trên data giả
2. Tính:
   - Human-Human Kappa
   - LLM-vs-Developer Kappa
   - Overall Kappa
   - OB Kappa
   - EB Kappa
   - S2R Kappa
   - Raw agreement
   - Label distribution
3. Kiểm tra phân phối output pilot có bất thường không
4. Ghi phát hiện vào `notes.md`

#### Tuần 8 - Full experiment

1. Chạy full statistical analysis
2. Giữ nguyên statistical test đã chọn trong proposal
3. Tính effect size
4. Điền `results/summary.csv` với:
   - metric value
   - p-value
   - effect size
   - N valid
   - N invalid
   - decision
5. Báo Huy xem mỗi RQ là reject hay fail to reject H0

### Quân - RW (Report Writer)

**Vai trò chính:**

- Giữ phần ghi chú và tài liệu rõ ràng
- Theo dõi các quyết định và vấn đề phát sinh
- Chuẩn bị wording cho figure và kết quả
- Hỗ trợ viết phần báo cáo cuối

**Những file Quân nên theo sát nhất:**

- `notes.md`
- `figures/README.md`
- các file write-up/báo cáo mà nhóm tạo thêm sau này

**Việc cụ thể của Quân:**

#### Tuần 7 - Pilot

1. Ghi lại quy trình pilot rõ ràng
2. Ghi lại các lỗi, lệch, hoặc quyết định trong `notes.md`
3. Hỗ trợ format kết quả pilot để nhóm review
4. Không tự đổi hướng nghiên cứu

#### Tuần 8 - Full experiment

1. Gom wording cho phần kết quả
2. Hỗ trợ viết caption cho figure
3. Hỗ trợ viết:
   - mô tả pilot result
   - mô tả full result
   - limitations
   - discussion

## 5. Flow công việc theo tuần

### Tuần 7 - Pilot

- Huy: check gate và chốt setup
- Hùng: tạo pilot sample và pilot ground truth
- Phúc: chạy pilot LLM
- Thêm: tính metric pilot
- Quân: ghi process và decision

### Tuần 8 - Full experiment

- Hùng: gán nhãn full dataset và verify IAA
- Phúc: chạy full LLM, log, checkpoint
- Thêm: tính full statistics và summary
- Quân: chuẩn bị figure và write-up
- Huy: review toàn bộ và quyết định chốt kết quả

## 6. Mỗi người phải nộp lại gì cho Huy

### Hùng nộp

- `data/pilot_sample.csv` đã điền
- `data/pilot_ground_truth.csv` đã điền
- `data/full_ground_truth.csv` đã điền
- IAA values và ghi chú

### Phúc nộp

- `results/pilot_llm_output.csv` đã điền
- `results/full_llm_output.csv` đã điền
- `results/pilot_api_log.txt`
- `results/full_api_log.txt`

### Thêm nộp

- kết quả metric
- `results/summary.csv` đã điền
- ghi chú pilot/full analysis

### Quân nộp

- `notes.md` đã cập nhật
- wording sạch cho pilot/full result
- caption hoặc figure note nếu có

## 7. Cảnh báo quan trọng

Nếu có một trong các trường hợp sau:

- kết quả thấp hơn threshold
- dataset ít hơn dự kiến
- API trả output lỗi format
- metric không tính được ở một số dòng

thì **không được giấu**, **không được sửa threshold**, và **không được cố làm đẹp kết quả**.  
Phải ghi rõ, đánh dấu invalid case, và báo lại cho Huy để xử lý đúng quy trình.
