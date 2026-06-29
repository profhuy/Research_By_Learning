# Phan Cua Huy - Lam Gi Truoc

File nay chi danh cho Huy de dieu phoi RBL-4 va RBL-5.

## 1. Viec Huy phai lam ngay

1. Tao GitHub repo chung cho nhom.
2. Up toan bo file trong pack nay len repo.
3. Gui link repo + `team-assignment-master.md` cho ca nhom.
4. Chot lai voi nhom la de tai khong doi:
   - Model: `GPT-4o mini`
   - Scope: `OB / EB / S2R`
   - Metric chinh: `Cohen's Kappa`
   - Threshold chinh: `Kappa >= 0.70`
5. Chi dinh ro tung nguoi nhan phan viec theo file tong.

## 2. Viec Huy tu lam duoc, khong can cho ai

- Tao GitHub repo.
- Upload pack RBL-4.
- Kiem tra lai cac file huong dan:
  - `rubric-ob-eb-s2r.md`
  - `prompt_final.md`
  - `pilot-workflow.md`
  - `week8-full-experiment.md`
- Tao nhanh hoac folder de nhom lam viec thong nhat.
- Mo `notes.md` va ghi:
  - ngay bat dau
  - deadline pilot
  - deadline full experiment
  - nguoi phu trach tung phan

## 3. Viec Huy phai cho du lieu tu nguoi khac

### Cho Hung

Huy chua the review pilot neu chua co:

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- random seed
- IAA pilot

Huy chua the cho chay full neu chua co:

- `data/full_ground_truth.csv`
- IAA full set

### Cho Phuc

Huy chua the quyet dinh pilot pass hay fail neu chua co:

- `results/pilot_llm_output.csv`
- `results/pilot_api_log.txt`

Huy chua the chot full run neu chua co:

- `results/full_llm_output.csv`
- `results/full_api_log.txt`

### Cho Them

Huy chua the ket luan ket qua neu chua co:

- Kappa overall
- Kappa cho `OB`
- Kappa cho `EB`
- Kappa cho `S2R`
- `results/summary.csv`

### Cho Quan

Huy chua nen viet phan ket qua cuoi neu chua co:

- ghi chu pilot/full trong `notes.md`
- wording cho result/discussion
- caption figure neu nhom co ve hinh

## 4. Thu tu cong viec dung

1. Huy tao repo va giao viec.
2. Hung chuan bi pilot sample + pilot ground truth.
3. Phuc chay pilot LLM tren sample cua Hung.
4. Them tinh metric pilot tu ground truth cua Hung + output cua Phuc.
5. Huy xem pilot co on de sang full khong.
6. Hung hoan tat full ground truth.
7. Phuc chay full experiment.
8. Them tinh full statistics va dien `results/summary.csv`.
9. Quan viet wording, notes, captions.
10. Huy review toan bo va chot ban nop.

## 5. Huy can yeu cau ca nhom nop lai gi

### Hung nop cho Huy

- `data/pilot_sample.csv`
- `data/pilot_ground_truth.csv`
- `data/full_ground_truth.csv`
- IAA pilot va IAA full

### Phuc nop cho Huy

- `results/pilot_llm_output.csv`
- `results/pilot_api_log.txt`
- `results/full_llm_output.csv`
- `results/full_api_log.txt`

### Them nop cho Huy

- metric pilot
- metric full
- `results/summary.csv`
- ket luan reject hay fail to reject H0

### Quan nop cho Huy

- `notes.md` da cap nhat
- wording cho pilot result
- wording cho full result
- limitations
- discussion notes

## 6. Huy chot pilot bang tieu chi nao

Pilot chi duoc qua neu:

- sample da co ground truth
- LLM chay dung prompt va dung model
- output parse duoc phan lon case
- metric tinh duoc
- khong co loi ky thuat lon

Neu pilot loi format, loi metric, hoac invalid qua nhieu thi chua duoc sang full.

## 7. Cau Huy co the gui nhom ngay

`Moi nguoi lam dung theo file team-assignment-master.md. Hien tai chua duoc doi de tai, model, metric hay threshold. Hung lam du lieu truoc, Phuc chay pilot sau khi co sample, Them tinh Kappa sau khi co output, Quan ghi notes va wording. Moi nguoi cap nhat file xong thi gui lai cho minh de minh review va quyet dinh sang full experiment.`
