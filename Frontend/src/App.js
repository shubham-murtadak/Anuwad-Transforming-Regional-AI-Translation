import React, { useState } from 'react';
import './app.css'; // Assuming your CSS is in App.css for styling
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowsAltH } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios'; // Import axios for API requests
import { Howl } from 'howler';

function App() {
    const [role, setRole] = useState('Student');
    const [status, setStatus] = useState('Idle');
    const [isListening, setIsListening] = useState(false);
    const [inputText, setInputText] = useState('');
    const [translatedText, setTranslatedText] = useState('');
    const [originalAudioUrl, setOriginalAudioUrl] = useState(''); // Renamed to match the state variable
    const [translatedAudioUrl, setTranslatedAudioUrl] = useState(''); // Renamed to match the state variable
    const [inputLanguage, setInputLanguage] = useState('en');
    const [outputLanguage, setOutputLanguage] = useState('hi');
    const [studentAudioUrl, setStudentAudioUrl] = useState('');
    const [teacherAudioUrl, setTeacherAudioUrl] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    // Full language names for dropdown display
    const languages = [' ', 'English', 'Hindi', 'Marathi', 'Kannada', 'Tamil', 'Telugu', 'Bangla'];

    // Language code mapping
    const languageMap = {
        'English': 'en',
        'Hindi': 'hi',
        'Marathi': 'mr',
        'Kannada': 'kn',
        'Tamil': 'ta',
        'Telugu': 'te',
        'Bangla': 'bn'
    };

    const playAudio = (url) => {
        console.log("This is the URL:", url);
    
        if (url) {
            try {
                const audio = new Audio(url);
                audio.play()
                    .then(() => {
                        console.log("Playing sound");
                    })
                    .catch((error) => {
                        console.error("Error playing sound:", error);
                    });
            } catch (error) {
                console.error("Error initializing audio:", error);
            }
        }
    };
    
    const toggleRole = async () => {
        try {
            setRole(role === 'Teacher' ? 'Student' : 'Teacher');

            const languageData = role === 'Teacher'
                ? {
                    inputLanguage: languageMap[outputLanguage],
                    outputLanguage: languageMap[inputLanguage]
                }
                : {
                    inputLanguage: languageMap[inputLanguage],
                    outputLanguage: languageMap[outputLanguage]
                };

            // Ensure response is correctly declared here
            const response = await axios.post('http://localhost:5000/stop_recording', languageData);

            setInputText(response.data.original_text);
            setTranslatedText(response.data.translated_text);
            setOriginalAudioUrl(response.data.input_audio_url); // Corrected to use the state variable
            setTranslatedAudioUrl(response.data.translated_audio_url); // Corrected to use the state variable

            // Set audio URLs based on who is speaking
            if (role === 'Student') {
                setStudentAudioUrl(response.data.input_audio_url); // Audio for student
                setTeacherAudioUrl(response.data.translated_audio_url); // Audio for teacher
            } else {
                setTeacherAudioUrl(response.data.input_audio_url); // Audio for teacher
                setStudentAudioUrl(response.data.translated_audio_url); // Audio for student
            }

        } catch (error) {
            console.error('Error in toggleRole', error);
        }
    };

    const startRecording = async () => {
        setStatus('Recording...');
        setIsListening(true); // Set role-specific listening status
        try {
            // Send the selected languages (input/output) based on the role
            const response = await axios.post('http://localhost:5000/start_recording', {
                inputLanguage: languageMap[inputLanguage], // Send input language code
                outputLanguage: languageMap[outputLanguage], // Send output language code
            });
            console.log(response.data);
        } catch (error) {
            console.error('Error starting recording', error);
        }
    };

    const stopRecording = async () => {
        setStatus('Processing...');
        try {
            const languageData = role === 'Teacher'
                ? {
                    inputLanguage: languageMap[outputLanguage], // Teacher's language as input (what teacher speaks)
                    outputLanguage: languageMap[inputLanguage]  // Student's language as output (what teacher wants to translate to)
                }
                : {
                    inputLanguage: languageMap[inputLanguage],   // Student's language as input (what student speaks)
                    outputLanguage: languageMap[outputLanguage]  // Teacher's language as output (what student wants to translate to)
                };

            // Send the request to stop recording and get the transcribed and translated text
            const response = await axios.post('http://localhost:5000/stop_recording', languageData);

            setInputText(response.data.original_text); // Set input text (transcribed text)
            setTranslatedText(response.data.translated_text); // Set translated text
            setOriginalAudioUrl(response.data.input_audio_url); // Set the URL of the original audio
            setTranslatedAudioUrl(response.data.translated_audio_url); // Set the URL of the translated audio

            // Set audio URLs based on who is speaking
            if (role === 'Student') {
                setStudentAudioUrl(response.data.input_audio_url); // Audio for student
                setTeacherAudioUrl(response.data.translated_audio_url); // Audio for teacher
            } else {
                setTeacherAudioUrl(response.data.input_audio_url); // Audio for teacher
                setStudentAudioUrl(response.data.translated_audio_url); // Audio for student
            }

            setStatus('Idle');
            setIsListening(false); // Reset listening status
        } catch (error) {
            console.error('Error stopping recording', error);
            setStatus('Idle');
        }
    };

    return (
        <div className="app-container">
            {/* Navbar */}
            <nav className="navbar">
                <div className="navbar-brand">
                    <img
                        src="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80"
                        alt="Anuwad Logo"
                        className="navbar-icon"
                    />
                    <span>Anuwad</span>
                </div>
                <div className="navbar-links">
                    <a href="#about">About</a>
                    <a href="#contactus">Contact Us</a>
                    <a href="#login">Login</a>
                </div>
            </nav>

            {/* Main Content */}
            <h1>🎓 Multilingual Translation System</h1>
            <div className="partition">
                {/* Teacher Section */}
                <div className={`section ${isListening && role === 'Teacher' ? 'listening' : ''}`}>
                    <h2>👩‍🏫 Teacher</h2>
                    <img src="/assets/teacher.jpg" alt="Teacher" className="role-image" />
                    <label>Language:</label>
                    <select
                        value={outputLanguage}
                        onChange={(e) => setOutputLanguage(e.target.value)}
                    >
                        {languages.map((lang) => (
                            <option key={lang} value={lang}>
                                {lang}
                            </option>
                        ))}
                    </select>

                    {/* Recording buttons */}
                    {role === 'Teacher' && !isListening && (
                        <button onClick={startRecording}>🎤 Start Recording</button>
                    )}
                    {role === 'Teacher' && isListening && (
                        <button onClick={stopRecording}>🔴 Stop Recording</button>
                    )}

                    {/* Display appropriate text based on the role */}
                    <div className="translated-text">
                        <textarea
                            value={role === 'Teacher' ? inputText : translatedText}
                            readOnly
                            placeholder={role === 'Teacher' ? "Your transcribed text will appear here..." : "Translated text will appear here..."}
                        />
                    </div>

                    {/* Audio Playback */}
                    <div className="audio-player">
                        <button className="audio-btn" onClick={() => playAudio(teacherAudioUrl)}>
                            🔊 Listen to {role === 'Teacher' ? 'Your Speech' : 'Translated Audio'}
                        </button>
                    </div>

                    <div className="status">
                        Status: {status === 'Recording...' ? '🔄 Recording...' : '✅ Idle'}
                    </div>
                </div>

                {/* Toggle Role Button (Positioned between sections) */}
                <div className="toggle-container">
                    <button onClick={toggleRole} className="toggle-role-btn">
                        <FontAwesomeIcon icon={faArrowsAltH} size="2x" />
                    </button>
                </div>

                {/* Student Section */}
                <div className={`section ${isListening && role === 'Student' ? 'listening' : ''}`}>
                    <h2>👨‍🎓 Student</h2>
                    <img src="/assets/student.jpg" alt="Student" className="role-image" />
                    <label>Language:</label>
                    <select
                        value={inputLanguage}
                        onChange={(e) => setInputLanguage(e.target.value)}
                    >
                        {languages.map((lang) => (
                            <option key={lang} value={lang}>
                                {lang}
                            </option>
                        ))}
                    </select>

                    {/* Recording buttons */}
                    {role === 'Student' && !isListening && (
                        <button onClick={startRecording}>🎤 Start Recording</button>
                    )}
                    {role === 'Student' && isListening && (
                        <button onClick={stopRecording}>🔴 Stop Recording</button>
                    )}

                    {/* Display appropriate text based on the role */}
                    <div className="translated-text">
                        <textarea
                            value={role === 'Student' ? inputText : translatedText}
                            readOnly
                            placeholder={role === 'Student' ? "Your transcribed text will appear here..." : "Translated text will appear here..."}
                        />
                    </div>

                    {/* Audio Playback */}
                    <div className="audio-player">
                        <button className="audio-btn" onClick={() => playAudio(studentAudioUrl)}>
                            🔊 Listen to {role === 'Student' ? 'Your Speech' : 'Translated Audio'}
                        </button>
                    </div>

                    <div className="status">
                        Status: {status === 'Recording...' ? '🔄 Recording...' : '✅ Idle'}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="footer">
                <p>&copy; 2024 Anuwad - Multilingual Translation System</p>
            </footer>
        </div>
    );
}

export default App;
