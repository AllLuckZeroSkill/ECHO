import React, { useState } from 'react';
import { View, Button, StyleSheet, Text } from 'react-native';
import Slider from '@react-native-community/slider';

const App = () => {
  const [showModes, setShowModes] = useState(false);
  const [sliderValue, setSliderValue] = useState(0);

  return (
    <View style={styles.container}>
      <View style={styles.box}>
        <Button
          title="Environmental Modes"
          color="#808080"
          onPress={() => setShowModes(!showModes)}
        />
      </View>

      {showModes && (
        <View style={styles.modeContainer}>
          <View style={styles.box}>
            <Button title="Social Mode" color="#808080" onPress={() => console.log('Social Mode')} />
          </View>
          <View style={styles.box}>
            <Button title="Commuting Mode" color="#808080" onPress={() => console.log('Commuting Mode')} />
          </View>
        </View>
      )}

      <View style={styles.sliderContainer}>
        <Text>Value: {sliderValue}</Text>
        <Slider
          style={{width: 300, height: 40}}
          minimumValue={0}
          maximumValue={100}
          minimumTrackTintColor="#808080"
          maximumTrackTintColor="#000000"
          onValueChange={(value) => setSliderValue(value)}
          value={sliderValue}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  box: {
    margin: 10,
    borderWidth: 1,
    borderColor: 'gray',
    borderRadius: 5,
  },
  modeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '80%',
    padding: 10,
  },
  sliderContainer: {
    marginTop: 20,
    alignItems: 'stretch',
    width: '80%',
  },
});

export default App;

