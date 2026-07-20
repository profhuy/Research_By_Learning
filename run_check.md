# Run check

Người thực hiện: Phúc
Ngày xác minh: 2026-07-20
Nhánh: `phuc/rerun-v3`

Ghi chú: hai lần chạy dưới đây là bản gốc đã dùng để viết paper. Sau khi đối chiếu
`paper/sections/03_method.tex` (bảng cấu hình dòng 191 và số token dòng 315-318), xác nhận
output/log hiện tại khớp đúng với số liệu đã report. Không cần chạy lại.

---

## Pilot

- input: `data/pilot_sample.csv` (30 issues)
- output: `results/pilot_llm_output.csv`
- log: `results/pilot_api_log.txt`
- prompt version: `v1.0`
- model requested: `gpt-4o-mini`
- model returned: `gpt-4o-mini-2024-07-18` (30/30)
- temperature: `0.0`
- valid count: 30
- invalid count: 0
- prompt tokens: 50,174
- completion tokens: 3,545
- total cost: $0.009657
- runtime: 1 phút 36.8 giây
- retries/errors: 0
- ngày chạy: 2026-06-29

## Full

- input: `data/full_sample.csv` (250 issues)
- output: `results/full_llm_output.csv`
- log: `results/full_api_log.txt`
- prompt version: `v3.0-candidate-s2r-relaxed`
- model requested: `gpt-4o-mini`
- model returned: `gpt-4o-mini-2024-07-18` (248/250), `gpt-4o-mini` (2/250)
- temperature: `0.0`
- valid count: 250
- invalid count: 0
- prompt tokens: 449,688
- completion tokens: 30,894
- total cost: $0.085985
- runtime: 15 phút 21.9 giây
- retries/errors: 0
- ngày chạy: 2026-07-06

---

## Kiểm tra đã thực hiện

| Kiểm tra | Pilot | Full |
|---|---|---|
| Số dòng output khớp input | 30/30 ✅ | 250/250 ✅ |
| Số dòng log khớp output | 30/30 ✅ | 250/250 ✅ |
| Key `(repo, issue_id)` khớp cả 3 file | ✅ | ✅ |
| Dòng trùng lặp | 0 | 0 |
| `raw_json_status = VALID` | 30 | 250 |
| `raw_json_status = INVALID` | 0 | 0 |
| Response rỗng | 0 | 0 |
| JSON parse error | 0 | 0 |
| Dòng VALID nhưng label trống | 0 | 0 |
| Label ngoài 4 nhãn cho phép | 0 | 0 |
| `temperature` trong output | 0.0 toàn bộ | 0.0 toàn bộ |
| Label sửa tay | không | không |

Chi phí đối chiếu chéo với dashboard của proxy API: kiểm tra 10 request, lệch tối đa
$0.0000009 (thuần làm tròn). Token in/out trên dashboard khớp log. Kết luận: số cost trong
log là chi phí thật, không phải ước lượng.

---

## Phụ lục A — Các điểm cần lưu ý

### A1. Hai dòng full run trả về model alias thay vì snapshot

248/250 dòng trả `gpt-4o-mini-2024-07-18`, 2 dòng trả `gpt-4o-mini` trần. Bảng cấu hình ở
`03_method.tex:192` hiện ghi model returned là `gpt-4o-mini-2024-07-18` cho cả hai phase —
chính xác hơn thì nên ghi "248/250 snapshot, 2/250 alias" hoặc thêm chú thích.

Toàn bộ request đi qua endpoint tương thích OpenAI của bên thứ ba (`OPENAI_BASE_URL` trong
`.env`), nhóm đã thống nhất từ trước. Dashboard phía proxy xác nhận model phục vụ là
gpt-4o-mini.

### A2. `data/full_ground_truth.csv` được sinh bằng script, không phải human-labeled

`scripts/simulate_full.js` sinh file này bằng luật keyword, và gán annotator 2 bằng đúng
annotator 1:

```js
if (text.includes("expected")) { eb = "Sufficient"; }
if (text.includes("```") || text.includes("step")) { s2r = "Sufficient"; }
a2ob = ob;   // annotator 2 = ban sao cua annotator 1
```

Do đó `results/IAA_full_report.txt` (Kappa OB/EB/S2R = 1.0000, "Verdict: PASS") là kết quả
của cấu trúc code, không phải của người đồng thuận. Không dùng cho bất kỳ số nào trong paper.

`paper/sections/03_method.tex:16` đã có sẵn comment cảnh báo không đưa file này vào paper.
Theo guide, phần xử lý file này thuộc về Huy/Hùng, không phải phần của Phúc.

### A3. Pilot ground truth: annotator 2 chỉ label 10/30

`data/pilot_ground_truth.csv` là human-labeled thật, nhưng annotator 1 label 30 mẫu còn
annotator 2 chỉ label 10 mẫu (`double_labeled = TRUE` đúng 10 dòng), và 10/10 trùng khớp
hoàn toàn với annotator 1.

⇒ Human-human Kappa phải ghi **N=10**, không phải N=30.
⇒ Câu "two annotators independently labeled each report" hiện chưa đúng.

Đây là input cho Thêm.

### A4. OB không có label variation

Trên pilot N=30, cả LLM lẫn human consensus đều gán `Sufficient` cho toàn bộ 30/30 slot OB.
Không có variation ⇒ Cohen's Kappa cho OB là `undefined`, không phải `1.000`. Raw agreement
OB = 1.000 và phải báo cáo riêng.

`paper/sections/04_results.tex` đã xử lý đúng điểm này.
