import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
example = root / '.env.example'
out = root / '.env'
if not example.exists():
    print('.env.example not found')
    raise SystemExit(1)

text = example.read_text()

secret = secrets.token_urlsafe(48)
jwt = secrets.token_urlsafe(48)
api = secrets.token_urlsafe(36)

text = text.replace('MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/randols_marketing?retryWrites=true&w=majority', 'MONGODB_URI=mongodb://localhost:27017/randols_marketing')
text = text.replace('SECRET_KEY=your-super-secret-key-change-in-production', f'SECRET_KEY={secret}')
text = text.replace('JWT_SECRET_KEY=your-jwt-secret-key-change-in-production', f'JWT_SECRET_KEY={jwt}')
text = text.replace('API_KEY=rnd_generate-a-secure-api-key-here', f'API_KEY={api}')

out.write_text(text)
print(f'Wrote {out}')
