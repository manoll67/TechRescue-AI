'use client';

import { useEffect, useRef, useState } from 'react';

const suggestions = [
    { icon: '▧', label: 'Windows', prompt: 'Компютърът ми с Windows работи много бавно.' },
    { icon: '⌘', label: 'Linux', prompt: 'Имам проблем с Wi-Fi на Linux.' },
    { icon: '◈', label: 'Хардуер', prompt: 'Как да проверя дали дискът ми е изправен?' },
    { icon: '⌁', label: 'Мрежи', prompt: 'Интернетът ми прекъсва постоянно.' },
];

const initialMessage = {
    sender: 'assistant',
    text: 'Здравей! Аз съм TechRescue. Опиши какво се случва с компютъра ти и ще ти помогна да подредиш следващите стъпки.',
};

export default function Home() {
    const [messages, setMessages] = useState([initialMessage]);
    const [question, setQuestion] = useState('');
    const [platform, setPlatform] = useState('Windows');
    const [notice, setNotice] = useState('');
    const inputRef = useRef(null);
    const chatRef = useRef(null);

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages]);

    function sendMessage(event) {
        event.preventDefault();
        const text = question.trim();

        if (!text) {
            setNotice('Напиши накратко какъв е проблемът.');
            inputRef.current?.focus();
            return;
        }

        setMessages((current) => [...current, { sender: 'user', text }]);
        setQuestion('');
        setNotice('Съобщението е добавено в демо интерфейса. AI услугата ще бъде свързана в следващ етап.');
    }

    function useSuggestion(prompt) {
        setQuestion(prompt);
        setNotice('');
        inputRef.current?.focus();
    }

    function startNewChat() {
        setMessages([initialMessage]);
        setQuestion('');
        setNotice('');
    }

    return (
        <main className="site-shell">
            <header className="topbar">
                <a className="brand" href="/" aria-label="TechRescue начало">
                    <span className="brand-mark" aria-hidden="true">
                        <svg viewBox="0 0 32 32" fill="none">
                            <path d="M16 3.5 26 7v7.7c0 6.2-4.1 11.7-10 13.8C10.1 26.4 6 20.9 6 14.7V7l10-3.5Z" />
                            <path d="m11.5 15.7 3 3 6.3-6.5" />
                        </svg>
                    </span>
                    <span className="brand-name">tech<span>rescue</span></span>
                </a>
                <div className="topbar-right">
                    <span className="stage-tag"><span className="status-dot" /> Frontend демо</span>
                    <a className="top-link" href="#how-it-works">Как работи</a>
                </div>
            </header>

            <section className="hero">
                <div className="eyebrow"><span className="sparkle">✳</span> ТЕХНИЧЕСКА ПОМОЩ, НА МОМЕНТА</div>
                <h1>Нека оправим проблема,<br /><span>стъпка по стъпка.</span></h1>
                <p className="hero-copy">Кажи ни какво не е наред. Ще започнем с най-важното и ще намерим решение заедно.</p>
            </section>

            <section className="workspace" aria-label="TechRescue чат">
                <div className="chat-panel">
                    <div className="chat-header">
                        <div className="assistant-identity">
                            <span className="assistant-avatar" aria-hidden="true">
                                <svg viewBox="0 0 24 24" fill="none">
                                    <path d="M12 3.5 19 6v5.4c0 4.3-2.9 8.1-7 9.6-4.1-1.5-7-5.3-7-9.6V6l7-2.5Z" />
                                    <path d="m9 12 2 2 4-4" />
                                </svg>
                            </span>
                            <div>
                                <div className="assistant-name">TechRescue помощник <span className="online-dot" /></div>
                                <div className="assistant-caption">Тук сме, за да помогнем</div>
                            </div>
                        </div>
                        <button className="new-chat-button" type="button" onClick={startNewChat}>
                            <span aria-hidden="true">＋</span> Нов разговор
                        </button>
                    </div>

                    <div className="chat-body" ref={chatRef} aria-live="polite">
                        {messages.map((message, index) => (
                            <div className={`message-row ${message.sender}`} key={`${message.sender}-${index}`}>
                                {message.sender === 'assistant' && <span className="message-avatar" aria-hidden="true">✳</span>}
                                <div className="message-bubble">
                                    {message.sender === 'assistant' && <div className="message-author">TechRescue <span>· помощник</span></div>}
                                    <p>{message.text}</p>
                                </div>
                                {message.sender === 'user' && <span className="user-avatar" aria-hidden="true">Т</span>}
                            </div>
                        ))}
                        {messages.length === 1 && (
                            <div className="suggestions" aria-label="Примери за проблеми">
                                <div className="suggestions-label">С какво имаш нужда от помощ?</div>
                                <div className="suggestions-grid">
                                    {suggestions.map((item) => (
                                        <button className="suggestion-card" key={item.label} type="button" onClick={() => useSuggestion(item.prompt)}>
                                            <span className="suggestion-icon" aria-hidden="true">{item.icon}</span>
                                            <span>{item.label}</span>
                                            <span className="suggestion-arrow" aria-hidden="true">↗</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    <form className="composer" onSubmit={sendMessage}>
                        <label className="sr-only" htmlFor="question">Опиши проблема си</label>
                        <textarea
                            id="question"
                            ref={inputRef}
                            value={question}
                            onChange={(event) => {
                                setQuestion(event.target.value);
                                if (notice) setNotice('');
                            }}
                            onKeyDown={(event) => {
                                if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
                                    sendMessage(event);
                                }
                            }}
                            placeholder="Опиши проблема си тук..."
                            rows={2}
                        />
                        <div className="composer-footer">
                            <div className="composer-options">
                                <span className="platform-label">Система:</span>
                                {['Windows', 'Linux'].map((item) => (
                                    <button
                                        className={`platform-chip ${platform === item ? 'selected' : ''}`}
                                        key={item}
                                        type="button"
                                        aria-pressed={platform === item}
                                        onClick={() => setPlatform(item)}
                                    >
                                        {item === 'Windows' ? '⊞' : '⌘'} {item}
                                    </button>
                                ))}
                            </div>
                            <button className="send-button" type="submit" aria-label="Изпрати съобщение">
                                <span>Изпрати</span>
                                <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M3.5 10h12m-5-5 5 5-5 5" /></svg>
                            </button>
                        </div>
                        {notice && <p className="notice" role="status">{notice}</p>}
                    </form>
                    <div className="privacy-note"><span aria-hidden="true">◇</span> Не споделяй пароли или друга лична информация.</div>
                </div>

                <aside className="side-panel">
                    <div className="side-card trust-card">
                        <div className="side-card-icon green-icon" aria-hidden="true">✓</div>
                        <h2>Помощ, на която можеш да разчиташ</h2>
                        <p>Разбираеми насоки за често срещани проблеми с компютъра.</p>
                        <div className="trust-divider" />
                        <div className="trust-point"><span>✓</span> Стъпка по стъпка</div>
                        <div className="trust-point"><span>✓</span> Windows и Linux</div>
                        <div className="trust-point"><span>✓</span> Без сложени термини</div>
                    </div>
                    <div className="side-card how-card" id="how-it-works">
                        <div className="how-heading"><span className="side-card-icon blue-icon" aria-hidden="true">i</span><h2>Как работи</h2></div>
                        <ol className="steps-list">
                            <li><span>1</span><div><strong>Опиши проблема</strong><small>Какво се случва и кога започна?</small></div></li>
                            <li><span>2</span><div><strong>Избери системата</strong><small>Windows или Linux.</small></div></li>
                            <li><span>3</span><div><strong>Следвай насоките</strong><small>Ще започнем от безопасните стъпки.</small></div></li>
                        </ol>
                    </div>
                    <div className="demo-card"><span className="demo-sparkle" aria-hidden="true">✳</span><p><strong>Предстои свързване с AI</strong><br />Това е първа версия на интерфейса. AI услугата ще се добави в следващ етап.</p></div>
                </aside>
            </section>

            <footer className="footer">
                <a className="brand footer-brand" href="/" aria-label="TechRescue начало">
                    <span className="brand-mark small-mark" aria-hidden="true">
                        <svg viewBox="0 0 32 32" fill="none"><path d="M16 3.5 26 7v7.7c0 6.2-4.1 11.7-10 13.8C10.1 26.4 6 20.9 6 14.7V7l10-3.5Z" /><path d="m11.5 15.7 3 3 6.3-6.5" /></svg>
                    </span>
                    <span className="brand-name">tech<span>rescue</span></span>
                </a>
                <span>Компютърна помощ, по-човешки.</span>
                <span>© 2026 TechRescue</span>
            </footer>
        </main>
    );
}
