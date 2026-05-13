import dotenv from 'dotenv';

dotenv.config();

export const config = {
  botToken: process.env.MAX_BOT_TOKEN || '',
  apiUrl: process.env.API_URL || 'http://localhost:8000/api',
  pageSize: 3,
};
