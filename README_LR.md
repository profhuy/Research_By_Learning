# RBL-4 — LLM Runner (Phúc)

Pipeline gọi GPT-4o mini chấm OB/EB/S2R cho bug report, theo đúng
`prompt_final.md` (v1.0). Config cố định: `model=gpt-4o-mini`,
`temperature=0.0`. Không tự sửa prompt/model/threshold.

Output/log đã làm để **khớp đúng template trên repo**
(`results/<mode>_llm_output.csv`, `results/<mode>_api_log.txt`).

## Đặt code vào repo ở đâu
Chạy LỆNH TỪ THƯ MỤC GỐC repo:
```
Research_By_Learning/
├── src/
│   ├── run_experiment.py
│   ├── llm_client.py
│   └── prompt_config.py
├── requirements.txt
├── .env.example
├── .gitignore          # repo đã có thì chỉ THÊM các dòng trong file này
├── data/               # đã có (pilot_sample.csv của Hùng)
└── results/            # đã có (template output + log)
```

## Cài đặt
```bash
pip install -r requirements.txt
```

## 1) Test offline NGAY (mock — không cần key, không tốn tiền)
```bash
python src/run_experiment.py --mode pilot --mock
```
- Đọc `data/pilot_sample.csv`, GIẢ LẬP câu trả lời LLM.
- Ghi ra `results/_mock/` (đã gitignore) -> KHÔNG đụng file thật trên repo.
- Dùng để kiểm tra pipeline + xác nhận môi trường local OK.

Test riêng đường xử lý INVALID (data giả có sentinel):
```bash
python src/run_experiment.py --mode pilot --mock --input data/pilot_sample_DUMMY.csv
```

## 2) Chạy THẬT (khi đã có key)
```bash
cp .env.example .env        # rồi mở .env, dán OPENAI_API_KEY thật vào
python src/run_experiment.py --mode pilot
```
- Tự động DỌN placeholder trong results/pilot_llm_output.csv và
  results/pilot_api_log.txt (xóa dòng trống / chú thích mẫu) trước khi ghi,
  nên output thật luôn sạch.
- ~30 call, tốn ~1 cent.

Tuần 8 (full): đặt data full vào data/full_sample.csv rồi --mode full.

## raw_json_status
- VALID   : JSON hợp lệ + đủ 3 thành phần + nhãn thuộc
  {Sufficient, Ambiguous, Missing, Incorrect}
- INVALID : empty_response / parse_error / schema_error / api_error
  -> dòng INVALID ĐỂ TRỐNG nhãn, không tự đoán. Lý do ghi ở log.

## Checkpoint / resume
Chạy lại sẽ bỏ qua issue đã có trong file output (so theo repo + issue_id),
an toàn khi đứt mạng / rate limit. Chạy lại từ đầu: xóa file output rồi chạy lại.

## Đồng bộ GitHub (sau pilot)
```bash
git add results/pilot_llm_output.csv results/pilot_api_log.txt
git commit -m "feat: add pilot LLM output (N=30)"
git push
```
Lưu ý: .env và results/_mock/ đã gitignore -> không lo lộ key / bẩn repo.

## Quyết định kỹ thuật (cần nhóm xác nhận)
- Tên hàm/biến snake_case (chuẩn Python).
- Bật JSON mode (response_format=json_object) - runtime config, KHÔNG sửa prompt.
- model trong CSV = gpt-4o-mini; model server trả về ghi ở log (response_model).
- Tên file input full: tạm đặt data/full_sample.csv - cần Hùng/Huy xác nhận.
