import {
  Avatar,
  Box,
  ChakraProvider,
  Grid,
  theme,
  VStack,
  Button,
  Select,
  Text,
  HStack,
  Link,
  Flex,
} from "@chakra-ui/react";
import { useState } from "react";
import axios from "axios";
import "./app.css"; // Custom styles

const backendApi = axios.create({
  baseURL: "http://localhost:5000", // Backend API URL
  headers: {
    "Content-Type": "application/json",
  },
});

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [originalText, setOriginalText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [audioUrl, setAudioUrl] = useState(""); // Store audio URL
  const [inputLanguage, setInputLanguage] = useState("hi-IN"); // Default to Hindi
  const [outputLanguage, setOutputLanguage] = useState("hi"); // Default to Hindi

  // Languages mapping
  const languages = {
    "hi-IN": "Hindi",
    "mr-IN": "Marathi",
    "kn-IN": "Kannada",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "en-US": "English",
    "es-ES": "Spanish",
  };

  // Safe version of languages
  const safeLanguages = languages || {};

  // Start Recording
  const startRecording = async () => {
    try {
      const response = await backendApi.post("/start_recording");
      if (response.data.status === "Recording started") {
        setIsRecording(true);
      }
    } catch (err) {
      console.error("Error starting recording:", err);
    }
  };

  // Stop Recording
  const stopRecording = async () => {
    try {
      setIsLoading(true);
      const response = await backendApi.post("/stop_recording", {
        inputLanguage,
        outputLanguage,
      });

      if (response.data.status === "Recording stopped") {
        setOriginalText(response.data.original_text);
        setTranslatedText(response.data.translated_text);
        setAudioUrl(response.data.audio_url); // Audio file URL
      }
    } catch (err) {
      console.error("Error stopping recording:", err);
    } finally {
      setIsRecording(false);
      setIsLoading(false);
    }
  };

  return (
    <ChakraProvider theme={theme}>
      <div className="app-container">
        <header className="navbar">
          <HStack spacing={4} align="center">
            <Avatar
              size="lg"
              name="Multilingual Translator"
              src="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80"
            />
            <h1 className="navbar-title">Anuwad</h1>
          </HStack>
          <HStack spacing={6} className="navbar-links">
            <Link href="#about" className="navbar-link">About</Link>
            <Link href="#contact" className="navbar-link">Contact Us</Link>
            <Link href="#login" className="navbar-link">Login</Link>
          </HStack>
        </header>
        <Grid minH="90vh" p={3} justifyContent="center">
          <VStack spacing={4} className="main-content" align="stretch">
            <Box className="language-selection">
              <Select
                placeholder="Select Input Language"
                value={inputLanguage}
                onChange={(e) => setInputLanguage(e.target.value)}
                className="select"
              >
                {Object.entries(safeLanguages).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </Select>
              <Select
                placeholder="Select Output Language"
                value={outputLanguage}
                onChange={(e) => setOutputLanguage(e.target.value)}
                className="select"
              >
                {Object.entries(safeLanguages).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </Select>
            </Box>
            <Box className="record-buttons">
              {!isRecording ? (
                <Button
                  colorScheme="teal"
                  size="sm" // Reduced button size
                  onClick={startRecording}
                  className="button"
                >
                  Start Recording
                </Button>
              ) : (
                <Button
                  colorScheme="red"
                  size="sm" // Reduced button size
                  onClick={stopRecording}
                  className="button"
                >
                  Stop Recording
                </Button>
              )}
            </Box>
            {isLoading && <Text fontSize="xl" color="gray.600">Processing...</Text>}
            {originalText && (
              <Box className="result-text" p={4} borderWidth={1} borderRadius="md" boxShadow="md" bg="gray.50">
                <Text fontWeight="bold" fontSize="lg" mb={2}>Original Text:</Text>
                <Text fontSize="xl" mb={4}>{originalText}</Text>
                <Text fontWeight="bold" fontSize="lg" mb={2}>Translated Text:</Text>
                <Text fontSize="xl" mb={4}>{translatedText}</Text>
                {audioUrl && (
                  <Box mt={4}>
                    <audio key={audioUrl} controls>
                      <source src={`http://localhost:5000${audioUrl}`} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  </Box>
                )}
              </Box>
            )}
          </VStack>
        </Grid>
      </div>
    </ChakraProvider>
  );
}

export default App;
