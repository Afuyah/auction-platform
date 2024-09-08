import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import AuctionRoom from './AuctionRoom';
import reportWebVitals from './reportWebVitals';

// Retrieve auctionId from the global window object
const auctionId = window.AUCTION_ID;
console.log('Auction ID from global:', auctionId);

// Check if the auctionId is a valid number
if (isNaN(auctionId) || auctionId <= 0) {
    console.error('Invalid Auction ID:', auctionId);
} else {
    console.log('Valid Auction ID:', auctionId);
}

const root = ReactDOM.createRoot(document.getElementById('auction-root'));

root.render(
  <React.StrictMode>
    <AuctionRoom auctionId={auctionId} />
  </React.StrictMode>
);

reportWebVitals();
