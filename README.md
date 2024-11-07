# Real-Time Auction System

A **high-performance, real-time auction platform** designed for seamless live bidding and immediate updates. Built using **Flask**, **Flask-SocketIO**, and **JWT authentication**, this platform enables secure, scalable, and highly interactive auction experiences. With real-time bid tracking and notification services, this solution ensures an optimal bidding environment, capable of supporting large user bases and high-frequency interactions.

---

## Key Features

- **Real-Time Bidding**: Powered by **Flask-SocketIO**, the platform offers bid updates in real time, supporting live interactions between bidders.
- **Secure Authentication**: **JWT (JSON Web Token)** authentication ensures secure session management and role-based access control for both bidders and administrators.
- **Auction Management**: Admin interface to manage auction items, control auction status, and view ongoing bid activities.
- **Live Notifications**: Bidders are instantly notified of bid status changes, new highest bids, auction close times, and winning bids.
- **Bid Management**: Users can place, view, and track bids in real time, providing transparent, up-to-date information for all participants.
- **Payment Integration**: Payments processed via integrated **PayPal API**, handling secure transactions for winning bids.

---

## Technology Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap
- **Database**: PostgreSQL, SQLite (for scalable storage and query optimization)
- **Authentication**: JWT for session handling and security
- **Real-Time Data**: Flask-SocketIO for real-time bid updates and notifications
- **Payment Integration**: PayPal API for processing winning bids and payments
- **DevOps**: Docker for containerization, GitHub Actions for CI/CD pipeline automation

---

## Installation and Setup

### Backend Setup

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/afuyah/auction-platform.git

2. Set Up Virtual Environment:
Navigate to the backend directory:
```
cd backend/
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install Dependencies:
```
pip install -r requirements.txt

```
4. Configure Database:
Set up your database (PostgreSQL or SQLite) and configure the DATABASE_URI in the .env file.


5. Run Flask Application:
```
flask run
```


Frontend Setup

1. Navigate to the Frontend Directory:
```
cd frontend/
```

2. Install Dependencies:
```
npm install
```

3. Start the Application:
```
npm start

```

Payment Integration

1. Set Up PayPal API:
Obtain PayPal API credentials and configure them in the .env file for secure payment processing.


2. Configure Webhooks:
Implement PayPal webhooks for payment status notifications.




---

How to Contribute

1. Fork the Repository:
Click the "Fork" button at the top-right of the repository page.


2. Clone Your Fork:
```
git clone https://github.com/afuyah/auction-platform.git
```

3. Create a Feature Branch:
```
git checkout -b feature-branch
```

4. Make Changes:
Implement new features or fix bugs.


5. Commit Changes:
```
git commit -am 'Add new feature'
```

6. Push to Your Fork:
```
git push origin feature-branch
```

7. Open a Pull Request:
Submit a pull request describing the changes made.




---

License

This project is licensed under the MIT License. See the LICENSE file for details.


---

Contact

For any inquiries, suggestions, or collaboration, feel free to reach out via email:
afuya.b@gmail.com.
---
