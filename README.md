# KYC OCR Finder

一个仅在本机运行的 macOS OCR 查找工具：从 KYC 图片和 PDF 中按姓名或证件号码检索资料。

> 安全提示：KYC 文件可能包含敏感个人资料。请勿把原始图片、PDF、OCR 结果或真实身份信息上传到 GitHub。

## 功能

- 递归扫描 JPG、JPEG、PNG 和 PDF
- 按证件号码（自动忽略横杠与空格）和姓名词组查找
- 支持并行 OCR 与实时进度
- `--rotate` 模式可检查四个旋转方向
- 仅在临时目录生成 OCR 中间文件，不修改原始 KYC 文档

## 安装

需要 macOS、Python 3 与 Homebrew Tesseract：

```bash
brew install tesseract
```

## 使用

```bash
python3 find_kyc.py \
  --root "$HOME/Desktop/upay/kyc" \
  --id "950926-10-5877" \
  --name "HASIM HAIRUL AIMAN ASYRAF BIN" \
  --workers 4
```

结果会显示在终端，并保存为 `ocr_matches.txt`。

如果证件照片可能横放或倒置，加入 `--rotate`：

```bash
python3 find_kyc.py \
  --root "$HOME/Desktop/upay/kyc" \
  --id "950926-10-5877" \
  --rotate
```

详细中文说明见 [README_CN.md](README_CN.md)。
