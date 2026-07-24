# Research_By_Learning

Kho lưu trữ này chứa dữ liệu, mã nguồn, kết quả thực nghiệm và bản thảo paper cho đề tài:

**Đánh giá GPT-4o mini như một công cụ tự động kiểm tra chất lượng bug report trên GitHub**

## Tổng Quan

Đề tài nghiên cứu khả năng sử dụng GPT-4o mini để hỗ trợ đánh giá chất lượng bug report trong các dự án mã nguồn mở. Trọng tâm của nghiên cứu là ba thành phần quan trọng đối với khả năng tái hiện lỗi:

- **Observed Behavior (OB):** hành vi thực tế quan sát được
- **Expected Behavior (EB):** hành vi mong đợi
- **Steps to Reproduce (S2R):** các bước tái hiện lỗi

Kết quả dự đoán của GPT-4o mini được so sánh với nhãn đồng thuận của annotator bằng **raw agreement** và **Cohen's Kappa**.

## Câu Hỏi Nghiên Cứu

GPT-4o mini có thể tự động đánh giá chất lượng bug report, xét theo mức độ đầy đủ của OB, EB và S2R, ở mức độ nào khi so sánh với annotator consensus bằng Cohen's Kappa?

## Dữ Liệu

Nghiên cứu sử dụng bug report từ ba repository mã nguồn mở trên GitHub:

- `pandas`
- `scikit-learn`
- `VS Code`

Bộ dữ liệu gồm:

- **30 bug reports** được gán nhãn thủ công để đánh giá agreement
- **250 bug reports** dùng để kiểm tra khả năng chạy pipeline ở quy mô lớn hơn

## Phương Pháp

Mỗi bug report được đánh giá theo ba chiều chất lượng: OB, EB và S2R.  
Mỗi chiều được gán một trong bốn nhãn:

- `Sufficient`
- `Ambiguous`
- `Missing`
- `Incorrect`

GPT-4o mini được chạy với cấu hình cố định:

- Model: `GPT-4o mini`
- Temperature: `0.0`
- Prompting: zero-shot, one independent request per report
- Output format: structured JSON

Kết quả của mô hình được so sánh với annotator consensus bằng:

- Raw agreement
- Cohen's Kappa

## Kết Quả Chính

| Chỉ số | Kết quả |
|---|---:|
| Overall raw agreement | 84.4% |
| Overall Cohen's Kappa | 0.582 |
| Ngưỡng chấp nhận | 0.60 |
| EB Kappa | 0.653 |
| S2R Kappa | 0.400 |
| Invalid output rate | 0.0% |

GPT-4o mini đạt agreement tổng thể gần với ngưỡng chấp nhận, nhưng chưa vượt qua ngưỡng `0.60`. Mô hình hoạt động tốt hơn ở phần **Expected Behavior**, trong khi **Steps to Reproduce** là điểm yếu chính.

## Kết Luận

GPT-4o mini phù hợp với vai trò công cụ hỗ trợ trong quy trình đánh giá chất lượng bug report. Mô hình có thể giúp maintainer sàng lọc các report có khả năng thiếu thông tin, nhưng chưa đủ tin cậy để thay thế hoàn toàn đánh giá của con người, đặc biệt khi kiểm tra các bước tái hiện lỗi.

## Cấu Trúc Thư Mục

```text
data/                 Dữ liệu bug report và các file mẫu
figures/              Hình ảnh, bảng biểu hoặc biểu đồ dùng trong paper
paper/                Mã nguồn LaTeX và bản paper cuối cùng
paper/sections/       Các section riêng của paper
paper/quality/        Log kiểm tra AI writing và ảnh chụp kết quả
results/              Kết quả chạy model và các file phân tích
