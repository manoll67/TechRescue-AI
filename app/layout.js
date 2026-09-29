import './globals.css';

export const metadata = {
    title: 'TechRescue — AI помощ за Windows и Linux',
    description: 'Ясна, стъпка по стъпка компютърна помощ за Windows и Linux.',
};

export default function RootLayout({ children }) {
    return (
        <html lang="bg">
            <body>{children}</body>
        </html>
    );
}
