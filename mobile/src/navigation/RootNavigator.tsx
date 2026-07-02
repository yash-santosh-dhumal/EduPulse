import React from 'react';
import { View, ActivityIndicator } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { AuthStack } from './AuthStack';
import { StudentTabs } from './StudentTabs';
import { TeacherTabs } from './TeacherTabs';
import { colors } from '../theme/colors';

export const RootNavigator = () => {
  const { user, isLoading } = useAuth();

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
      <ActivityIndicator size="large" color={colors.danger} />
    </View>
  );
};
