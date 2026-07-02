import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useAuth } from '../../context/AuthContext';
import { colors, spacing } from '../../theme/colors';

export const StudentDashboard = () => {
  const { user, logout } = useAuth();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome, {user?.name}</Text>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Upcoming Assignments</Text>
        <Text style={styles.cardText}>You have 2 pending assignments.</Text>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.m,
  },
  title: {
    color: colors.text,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: spacing.l,
  },
  card: {
    backgroundColor: colors.surface,
    padding: spacing.m,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.m,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  cardText: {
    color: colors.textMuted,
  },
  logoutButton: {
    marginTop: 'auto',
    backgroundColor: colors.surfaceHighlight,
    padding: spacing.m,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutText: {
    color: colors.danger,
    fontWeight: 'bold',
  }
});
