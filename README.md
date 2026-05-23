# Kidney CT Classifier Website

Static project website for the mini project **Kidney Tumor Detection in CT Scans Using 2D CNN and Transformer Networks**.

## Run Locally With Real Prediction

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:8000/
```

The upload section calls the trained ResNet18 model at `/api/predict`.

## Deploy Quickly

### GitHub Pages

1. Create a new GitHub repository.
2. Upload `index.html`, `styles.css`, `script.js`, and `README.md`.
3. Go to repository **Settings > Pages**.
4. Choose **Deploy from a branch**, select `main`, and save.
5. GitHub will provide a public website link.

### Netlify

1. Go to <https://app.netlify.com/drop>.
2. Drag this project folder into the upload area.
3. Netlify will instantly create a public URL.

Netlify Drop only hosts the static website. It will not run the PyTorch model backend.

### Vercel

1. Go to <https://vercel.com/new>.
2. Import the repository or drag/upload the folder.
3. Keep the default static site settings and deploy.

Vercel static hosting also will not run this PyTorch backend without extra serverless setup.

### Render for Real Model Prediction

Use this option when the uploaded image must be evaluated by the trained model online.

1. Push this folder to GitHub.
2. Go to <https://render.com>.
3. Create a new **Web Service** from the GitHub repository.
4. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. Deploy and open the Render URL.
