# RBL-4 Checklist — 7 Gates

Tất cả gates phải pass trước khi bắt đầu pilot (Tuần 7).

- [ ] **E1 — Proposal duyệt**: GV confirm hoặc email xác nhận
- [ ] **E2 — Dataset**: File thật có trong `data/raw/`, đúng format, có README.md
- [ ] **E3 — API test**: `scripts/test_api.py` chạy được, có 1 output mẫu
- [ ] **E4 — Metric script**: `scripts/compute_iaa.py` chạy trên data giả, không lỗi
- [ ] **E5 — Ground truth plan**: Proposal §5.4 có annotation process + ngưỡng IAA
- [ ] **E6 — Budget**: Chi phí ước tính ≤ ngân sách có sẵn
- [ ] **E7 — GitHub**: Repo có, tất cả thành viên push được, `.gitignore` đúng
