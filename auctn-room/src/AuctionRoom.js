import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import './AuctionRoom.css';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

const socket = io();

const AuctionRoom = ({ auctionId }) => {
    const [currentPrice, setCurrentPrice] = useState(0);
    const [endTime, setEndTime] = useState('');
    const [messages, setMessages] = useState([]);
    const [bidAmount, setBidAmount] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [timer, setTimer] = useState('');

    useEffect(() => {
        console.log('AuctionRoom useEffect triggered with auctionId:', auctionId);

        if (!auctionId) {
            console.error('Auction ID is not available');
            return;
        }

        console.log('Joining auction room:', auctionId);
        socket.emit('join', { auction_id: auctionId });

        socket.on('status', (data) => {
            console.log('Received status update:', data);
            setCurrentPrice(data.current_price);
            setEndTime(data.end_time);
            setMessages(prevMessages => [...prevMessages, data.message]);
            startCountdown(data.end_time);
        });

        socket.on('bid_status', (data) => {
            console.log('Received bid status update:', data);
            if (data.success) {
                setCurrentPrice(data.new_bid_amount);
                setMessages(prevMessages => [...prevMessages, data.message]);
            } else {
                setErrorMessage(data.message);
                setMessages(prevMessages => [...prevMessages, data.message]);
            }
        });

        socket.on('auction_extended', (data) => {
            console.log('Received auction extension:', data);
            setEndTime(data.new_end_time);
            setMessages(prevMessages => [...prevMessages, data.message]);
            startCountdown(data.new_end_time);
        });

        socket.on('error', (data) => {
            console.log('Received error:', data);
            setErrorMessage(data.message);
            setMessages(prevMessages => [...prevMessages, data.message]);
        });

        return () => {
            socket.disconnect();
            if (timer) clearInterval(timer);
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
        if (timer) clearInterval(timer);

        const endDate = new Date(endTime);
        const updateTimer = () => {
            const now = new Date();
            const timeLeft = endDate - now;

            if (timeLeft <= 0) {
                setEndTime('Auction Ended');
                clearInterval(timer);
                return;
            }

            const minutes = Math.floor(timeLeft / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            setTimer(`${minutes}m ${seconds}s`);
        };

        updateTimer();
        setTimer(setInterval(updateTimer, 1000));
    };

    return (
        <div className="auction-room">
            <div className="auction-item">
                <h2>Auction Item</h2>
                <div className="item-image">
                    <Canvas>
                        <OrbitControls />
                        <Model path={`/static/auction-item-${auctionId}.glb`} />
                    </Canvas>
                </div>
                <div className="current-price">
                    Current Price: ${currentPrice}
                </div>
                <div className="end-time">
                    Time Remaining: {endTime === 'Auction Ended' ? endTime : timer}
                </div>
            </div>

            <div className="bidding-section">
                <input
                    type="number"
                    value={bidAmount}
                    onChange={(e) => setBidAmount(e.target.value)}
                    placeholder="Enter your bid amount"
                    min={parseFloat(currentPrice) + 1}
                />
                <button onClick={handleBid} disabled={!bidAmount}>Place Bid</button>
            </div>

            <div className="feedback-section">
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

const Model = ({ path }) => {
    const { scene } = useGLTF(path);
    return <primitive object={scene} />;
};

export default AuctionRoom;
