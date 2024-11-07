# Coastal Region Property Rental Platform (Airbnb Clone)

A comprehensive property rental platform tailored for the Kenyan coastal region. This platform mimics the functionality of popular platforms like Airbnb, enabling property owners to list and manage their properties, and renters to browse, book, and make payments securely.

---

## Key Features

- **Property Listings**: Browse detailed property information including location, price, amenities, and images.
- **Booking Management**: Users can check availability, make bookings, and receive booking confirmations.
- **Secure Payment Integration**: Payment gateways (PayPal, M-Pesa) for seamless and secure transactions.
- **Dynamic Pricing**: Flexible pricing with support for seasonal rates, discounts, and special offers.
- **User Authentication**: Role-based user management for property owners, renters, and admins, with secure login via **JWT**.
- **Admin Dashboard**: Manage users, properties, and bookings with real-time data insights.
  
---

## Technology Stack

- **Frontend**: React.js
- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Payment Integration**: PayPal, M-Pesa
- **Security**: JWT Authentication, HTTPS, Secure Payment Processing

---

## Setup and Installation

1. **Clone the Repository**:  
   `git clone https://github.com/yourusername/coastal-property-rental.git`
   
2. **Backend Setup**:
   - Navigate to the backend directory:  
     `cd backend/`
   - Create and activate a virtual environment:  
     `python -m venv venv`  
     `source venv/bin/activate` (Mac/Linux)  
     `venv\Scripts\activate` (Windows)
   - Install dependencies:  
     `pip install -r requirements.txt`
   - Set up the database and configure environment variables (see `.env` file for configuration).
   - Run the Flask app:  
     `flask run`
   
3. **Frontend Setup**:
   - Navigate to the frontend directory:  
     `cd frontend/`
   - Install dependencies:  
     `npm install`
   - Run the React app:  
     `npm start`

4. **Payment Configuration**:  
   - Set up your **PayPal** and **M-Pesa** credentials in the environment variables to enable secure payment transactions.

---

## How to Contribute

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Submit a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For any queries or suggestions, feel free to open an issue or contact me via [afuya.b@gmail.com](mailto:afuya.b@gmail.com).

---
