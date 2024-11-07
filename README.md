# Real-Time Auction System

A dynamic **real-time auction platform** built using **Flask** and **Flask-SocketIO**, designed for live bidding with instant updates. The system supports **secure user authentication**, **bid management**, and **real-time notifications**. Ideal for scenarios where high-frequency interactions are required, such as online auctions, sales, or bidding events.

---

## Key Features

- **Real-Time Bidding**: Utilizes **Flask-SocketIO** for live bid updates, allowing multiple users to participate in the auction simultaneously.
- **Secure User Authentication**: Implemented using **JWT** for session management, ensuring secure access for bidders and administrators.
- **Auction Management**: Admin interface for managing auction items, starting, ending, and reviewing auction results.
- **Bid Management**: Users can place bids, track ongoing auctions, and view the highest bid in real time.
- **Notifications**: Instant notifications for new bids, winning bid, auction start and end, and other key actions.
- **Payment Integration**: Configured with secure payment gateways (e.g., PayPal) for handling winning bids and payments.
  
---

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap
- **Backend**: Python (Flask), Flask-SocketIO
- **Database**: PostgreSQL, SQLite
- **Authentication**: JWT Authentication
- **Real-Time Updates**: Flask-SocketIO for live data broadcasting
- **Payment Integration**: PayPal (for winning bid payments)

---

## Setup and Installation

### Backend Setup

1. **Clone the Repository**:  
   `git clone https://github.com/yourusername/auction-platform.git`
   
2. **Create a Virtual Environment**:  
   Navigate to the backend directory:  
   `cd backend/`  
   Create and activate the virtual environment:  
   `python -m venv venv`  
   `source venv/bin/activate` (Mac/Linux)  
   `venv\Scripts\activate` (Windows)

3. **Install Dependencies**:  
   `pip install -r requirements.txt`
   
4. **Configure Database**:  
   Set up your PostgreSQL or SQLite database by configuring the `DATABASE_URI` in the `.env` file.

5. **Run the Flask App**:  
   `flask run`

### Frontend Setup

1. **Navigate to the Frontend**:  
   `cd frontend/`

2. **Install Dependencies**:  
   `npm install`

3. **Run the Application**:  
   `npm start`

### Payment Integration

- Set up **PayPal API** credentials for payment processing of winning bids.
- Configure payment API keys in the `.env` file for smooth transaction handling.

---

## How to Contribute

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push your branch (`git push origin feature-branch`).
5. Create a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For any inquiries or suggestions, feel free to open an issue or contact me at [afuya.b@gmail.com](mailto:afuya.b@gmail.com).

---
