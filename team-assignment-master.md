# RBL-4 - File Tong Hop Phan Cong Nhom

Day la file dieu phoi chinh cho ca nhom.
Tat ca thanh vien nen doc file nay truoc khi bat dau lam RBL-4.

## 1. Huong nghien cuu co dinh

Nhom phai bam dung `proposal RBL-3` da duoc duyet.

- De tai: dung `GPT-4o mini` nhu mot quality gate de danh gia bug report tren GitHub OSS
- Pham vi danh gia: `OB / EB / S2R`
- Metric chinh: `Cohen's Kappa`
- Threshold chinh: `Kappa >= 0.70`

## 2. Nguyen tac chung cho ca nhom

- Khong tu doi `RQ`, `metric`, `threshold`, hoac `model`.
- Khong tu sua rubric neu chua thong nhat trong nhom.
- Khong tu doi prompt neu chua ghi amendment ro rang.
- Phai lam `pilot` truoc, on roi moi chay `full experiment`.
- Moi output quan trong deu phai luu lai va dong bo ve GitHub.

## 3. Cac file chung moi nguoi phai biet

### File dieu phoi chinh

- `README.md`
- `HUY_WORKPLAN.md`
- `GITHUB_SETUP.md`
- `rubric-ob-eb-s2r.md`
- `prompt_final.md`
- `pilot-workflow.md`
- `week8-full-experiment.md`
- `issue-handling-rules.md`
- `sync-results-to-github.md`

### File du lieu va ket qua mau

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`
- `results/pilot_llm_output.csv`
- `results/full_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_api_log.txt`
- `results/summary.csv`

## 4. Phan cong theo tung thanh vien

### Huy - PL (Project Lead)

Vai tro chinh:

- Giu thu muc master va ban cuoi cua tat ca file
- Kiem tra cac gate bat buoc truoc khi chay pilot
- Chot rubric cuoi va prompt cuoi
- Quyet dinh pilot da du on de sang full experiment hay chua
- Quyet dinh co can amendment hay khong
- Theo doi deadline va gom output cua ca nhom

File Huy can theo sat nhat:

- `HUY_WORKPLAN.md`
- `GITHUB_SETUP.md`
- `rubric-ob-eb-s2r.md`
- `prompt_final.md`
- `results/summary.csv`

Viec cu the cua Huy:

1. Xac nhan ca nhom chi bam proposal da duyet.
2. Tao GitHub repo chung.
3. Dua toan bo pack nay len repo.
4. Giao viec ro rang cho tung nguoi.
5. Review ket qua pilot truoc khi cho sang Tuan 8.
6. Review output full experiment truoc khi viet bao cao cuoi.

### Hung - DG (Data and Ground Truth)

Vai tro chinh:

- Chuan bi pilot sample
- Chuan bi full dataset
- Gan nhan du lieu
- Tao consensus label cua developer
- Kiem tra IAA

File Hung phu trach:

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`

### Phuc - LR (LLM Runner)

Vai tro chinh:

- Chuan bi pipeline goi API
- Chay GPT-4o mini tren pilot
- Chay GPT-4o mini tren full dataset
- Luu output va log can than

File Phuc phu trach:

- `results/pilot_llm_output.csv`
- `results/full_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_api_log.txt`

### Them - MS (Metrics and Statistics)

Vai tro chinh:

- Xac nhan script metric chay duoc
- Tinh toan bo metric o pilot
- Tinh toan bo metric o full experiment
- Chuan bi bang summary va dien giai thong ke

File Them phu trach:

- `results/pilot_analysis_plan.md`
- `results/summary.csv`

### Quan - RW (Report Writer)

Vai tro chinh:

- Giu phan ghi chu va tai lieu ro rang
- Theo doi cac quyet dinh va van de phat sinh
- Chuan bi wording cho figure va ket qua
- Ho tro viet phan bao cao cuoi

File Quan nen theo sat nhat:

- `notes.md`
- `figures/README.md`

## 5. Ai lam truoc, ai lam sau

Thu tu dung de khong bi nghen viec:

1. Huy tao GitHub repo va giao viec.
2. Hung lam `data/pilot_sample.csv` va `data/pilot_ground_truth.csv`.
3. Phuc chi bat dau sau khi Hung da xong pilot sample.
4. Them chi bat dau tinh pilot sau khi co:
   - ground truth tu Hung
   - output pilot tu Phuc
5. Huy review pilot va quyet dinh co sang full hay khong.
6. Hung hoan tat `data/full_ground_truth.csv`.
7. Phuc chay full experiment.
8. Them tinh full statistics va dien `results/summary.csv`.
9. Quan viet wording, notes, captions sau khi da co so lieu.
10. Huy review va chot ban cuoi.

## 6. Phan Huy phai lam ngay

1. Tao GitHub repo.
2. Dua toan bo pack nay len repo.
3. Gui `team-assignment-master.md`, `HUY_WORKPLAN.md`, `GITHUB_SETUP.md` cho nhom.
4. Nhac lai de tai co dinh:
   - `GPT-4o mini`
   - `OB / EB / S2R`
   - `Cohen's Kappa`
   - `Kappa >= 0.70`
5. Thu output cua tung nguoi va review truoc khi sang buoc tiep theo.

## 7. Moi nguoi phai nop lai gi cho Huy

### Hung nop

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`
- IAA pilot va IAA full

### Phuc nop

- `results/pilot_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_llm_output.csv`
- `results/full_api_log.txt`

### Them nop

- metric pilot
- metric full
- `results/summary.csv`
- ket luan reject hay fail to reject H0

### Quan nop

- `notes.md` da cap nhat
- wording cho pilot result
- wording cho full result
- limitations
- discussion notes

## 8. Canh bao quan trong

Neu co mot trong cac truong hop sau:

- ket qua thap hon threshold
- dataset it hon du kien
- API tra output loi format
- metric khong tinh duoc o mot so dong

thi khong duoc giau, khong duoc sua threshold, va khong duoc co lam dep ket qua.
Phai ghi ro, danh dau invalid case, va bao lai cho Huy de xu ly dung quy trinh.
