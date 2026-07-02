import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing } from '../../theme/colors';

export const AttendanceMarkingScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.emptyText}>Select a class to mark attendance.</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.m,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 16,
  }
});
