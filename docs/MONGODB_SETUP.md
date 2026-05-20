# MongoDB Atlas Setup Guide for Clazzy

## Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up with Google/Email
3. Choose **FREE tier** (M0 Sandbox)
4. Select cloud provider: **AWS** (recommended)
5. Region: Choose closest to you (e.g., Mumbai for India)
6. Cluster Name: **ClazzyDB**
7. Click **Create Deployment**

## Step 2: Create Database User

1. Go to **Database Access** (left sidebar)
2. Click **Add New Database User**
3. Authentication Method: **Password**
4. Username: `clazzy_admin`
5. Password: Generate a secure password (save it!)
6. Database User Privileges: **Atlas Admin**
7. Click **Add User**

## Step 3: Configure Network Access

1. Go to **Network Access** (left sidebar)
2. Click **Add IP Address**
3. Choose **Allow Access from Anywhere** (0.0.0.0/0)
   - For production, use specific IPs
4. Click **Confirm**

## Step 4: Get Connection String

1. Go to **Database** (left sidebar)
2. Click **Connect** on your cluster
3. Choose **Drivers**
4. Select: **Node.js** / Version: **6.0 or later**
5. Copy connection string:
   ```
   mongodb+srv://clazzy_admin:<password>@clazzydb.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password
7. Add database name: `mongodb+srv://clazzy_admin:yourpassword@clazzydb.xxxxx.mongodb.net/clazzy?retryWrites=true&w=majority`

## Step 5: Add to .env File

Create/update `.env` file in project root:
```
MONGODB_URI=mongodb+srv://clazzy_admin:yourpassword@clazzydb.xxxxx.mongodb.net/clazzy?retryWrites=true&w=majority
```

## You're Ready! 🎉

Now continue with the code implementation below.
