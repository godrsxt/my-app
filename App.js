// App.js
import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Dimensions,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';

const paragraphs = {
  "Pangram 1": "The quick brown fox jumps over the lazy dog.",
  "Pangram 2": "Pack my box with five dozen liquor jugs.",
  "Pangram 3": "Jinxed wizards pluck ivy from the big quilt.",
  "Pangram 4": "Sphinx of black quartz, judge my vow.",
  "Lorem Ipsum": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
  "Shakespeare": "To be, or not to be, that is the question. Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune."
};

const TypingTest = () => {
  const [selectedParagraph, setSelectedParagraph] = useState("");
  const [currentText, setCurrentText] = useState("");
  const [targetText, setTargetText] = useState("Press 'Start Test' to begin");
  const [isTestActive, setIsTestActive] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [stats, setStats] = useState({ wpm: 0, accuracy: 0 });
  const inputRef = useRef(null);

  const calculateStats = (inputText) => {
    if (!isTestActive || !startTime) return;

    const totalChars = inputText.length;
    const correctChars = [...inputText].reduce((acc, char, i) => {
      return acc + (i < targetText.length && char === targetText[i] ? 1 : 0);
    }, 0);

    const accuracy = (correctChars / Math.max(1, totalChars)) * 100;
    const elapsedTime = (Date.now() - startTime) / 1000 / 60; // in minutes
    const wpm = (totalChars / 5) / Math.max(elapsedTime, 0.01);

    setStats({
      wpm: Math.round(wpm),
      accuracy: accuracy.toFixed(1)
    });

    if (inputText.length >= targetText.length) {
      finishTest();
    }
  };

  const startTest = () => {
    if (!selectedParagraph) {
      setTargetText("Please select a paragraph first!");
      return;
    }

    setCurrentText("");
    setStartTime(Date.now());
    setIsTestActive(true);
    setStats({ wpm: 0, accuracy: 0 });
    inputRef.current?.focus();
  };

  const finishTest = () => {
    setIsTestActive(false);
  };

  const onParagraphSelect = (value) => {
    setSelectedParagraph(value);
    setTargetText(paragraphs[value]);
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.targetTextContainer}>
        <Text style={styles.targetText}>{targetText}</Text>
      </ScrollView>

      <TextInput
        ref={inputRef}
        style={styles.input}
        multiline={false}
        value={currentText}
        onChangeText={(text) => {
          setCurrentText(text);
          calculateStats(text);
        }}
        editable={isTestActive}
        placeholder="Type here when test starts..."
      />

      <Text style={styles.stats}>
        WPM: {stats.wpm} | Accuracy: {stats.accuracy}%
      </Text>

      <TouchableOpacity
        style={styles.button}
        onPress={startTest}
      >
        <Text style={styles.buttonText}>
          {isTestActive ? "Test in Progress" : "Start Test"}
        </Text>
      </TouchableOpacity>

      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={selectedParagraph}
          onValueChange={onParagraphSelect}
          style={styles.picker}
        >
          <Picker.Item label="Select Paragraph" value="" />
          {Object.keys(paragraphs).map((key) => (
            <Picker.Item key={key} label={key} value={key} />
          ))}
        </Picker>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  targetTextContainer: {
    maxHeight: 100,
    marginBottom: 20,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 5,
  },
  targetText: {
    fontSize: 18,
    lineHeight: 24,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    fontSize: 18,
    marginBottom: 20,
  },
  stats: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    marginBottom: 20,
  },
  picker: {
    height: 50,
  },
});

export default TypingTest;