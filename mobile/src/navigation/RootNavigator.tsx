import React from 'react';
import { View, ActivityIndicator, TouchableOpacity, Text } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { AuthStack } from './AuthStack';
import { StudentTabs } from './StudentTabs';
import { TeacherTabs } from './TeacherTabs';
import { colors } from '../theme/colors';

export const RootNavigator = () => {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!user) {
    return <AuthStack />;
  }

  if (user.role === 'student') {
    return <StudentTabs />;
  } else if (user.role === 'teacher') {
    return <TeacherTabs />;
  }

  // Fallback for admin or unhandled roles on mobile
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background }}>
      <Text style={{ color: colors.text, marginBottom: 20, fontSize: 18 }}>Admin Dashboard (Web Only)</Text>
      <TouchableOpacity 
        onPress={logout}
        style={{ padding: 12, backgroundColor: colors.surfaceHighlight, borderRadius: 8 }}
      >
        <Text style={{ color: colors.danger, fontWeight: 'bold' }}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
};
