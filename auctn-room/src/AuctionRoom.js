import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import './AuctionRoom.css';

const socket = io();

const AuctionRoom = ({ auctionId }) => {
    console.log('Auction ID inside AuctionRoom:', auctionId); 

    const [currentPrice, setCurrentPrice] = useState(0);
    const [endTime, setEndTime] = useState('');
    const [messages, setMessages] = useState([]);
    const [bidAmount, setBidAmount] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [timerText, setTimerText] = useState('');
    const [timerInterval, setTimerInterval] = useState(null);

    useEffect(() => {
        console.log('AuctionRoom useEffect triggered with auctionId:', auctionId);

        if (!auctionId) {
            console.error('Auction ID is not available');
            return;
        }

        console.log('Joining auction room:', auctionId);
        // Join the auction room
        socket.emit('join', { auction_id: auctionId });

        // Listen for auction status updates
        socket.on('status', (data) => {
            console.log('Received status update:', data);
            setCurrentPrice(data.current_price);
            setEndTime(data.end_time);
            setMessages(prevMessages => [...prevMessages, data.message].slice(-3)); // Keep only last 3 messages
            startCountdown(data.end_time);
        });

        // Listen for bid status updates
        socket.on('bid_status', (data) => {
            console.log('Received bid status update:', data);
            if (data.success) {
                setCurrentPrice(data.new_bid_amount);
                setMessages(prevMessages => [...prevMessages, data.message].slice(-3)); // Keep only last 3 messages
            } else {
                setErrorMessage(data.message);
                setMessages(prevMessages => [...prevMessages, data.message].slice(-3)); // Keep only last 3 messages
            }
        });

        // Listen for auction extension
        socket.on('auction_extended', (data) => {
            console.log('Received auction extension:', data);
            setEndTime(data.new_end_time);
            setMessages(prevMessages => [...prevMessages, data.message].slice(-3)); // Keep only last 3 messages
            startCountdown(data.new_end_time);
        });

        // Listen for errors
        socket.on('error', (data) => {
            console.log('Received error:', data);
            setErrorMessage(data.message);
            setMessages(prevMessages => [...prevMessages, data.message].slice(-3)); // Keep only last 3 messages
        });

        // Clean up on component unmount
        return () => {
            socket.disconnect();
            if (timerInterval) clearInterval(timerInterval);
        };
    }, [auctionId]);

    const handleBid = () => {
        if (bidAmount) {
            setErrorMessage('');
            socket.emit('bid', { auction_id: auctionId, bid_amount: bidAmount });
            setBidAmount('');
        } else {
            setErrorMessage('Bid amount is required.');
        }
    };

    const startCountdown = (endTime) => {
        if (timerInterval) clearInterval(timerInterval);

        const endDate = new Date(endTime);
        const updateTimer = () => {
            const now = new Date();
            const timeLeft = endDate - now;

            if (timeLeft <= 0) {
                setTimerText('Auction Ended');
                clearInterval(timerInterval);
                return;
            }

            const minutes = Math.floor(timeLeft / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            setTimerText(`${minutes}m ${seconds}s`);
        };

        updateTimer();
        setTimerInterval(setInterval(updateTimer, 1000));
    };

    return (
        <div className="auction-room">
            <div className="auction-item">
                <h3>Live Item</h3>
                <div className="item-image">
                    <img src={`/static/auction-item-${auctionId}.jpg`} alt="Auction Item" />
                </div>
                <div className="current-price">
                    Current Price: ${currentPrice}
                </div>
                <div className="end-time">
                    Time Remaining: {endTime === 'Auction Ended' ? endTime : timerText}
                </div>
            </div>

            <div className="bidding-section">
                <input
                    type="number"
                    value={bidAmount}
                    onChange={(e) => setBidAmount(e.target.value)}
                    placeholder=" Bid Amount"
                    min={parseFloat(currentPrice) + 5}
                />
                <button onClick={handleBid} disabled={!bidAmount}>Place Bid</button>
            </div>

            <div className="feedback-panel">
                {errorMessage && <div className="feedback-error">{errorMessage}</div>}
                {messages.map((msg, index) => (
                    <div key={index} className="feedback-message">
                        {msg}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AuctionRoom;
