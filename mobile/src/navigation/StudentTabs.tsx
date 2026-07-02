import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StudentDashboard } from '../screens/student/StudentDashboard';
import { NotificationsScreen } from '../screens/common/NotificationsScreen';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();

export const StudentTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.text,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSubtle,
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={StudentDashboard} 
        options={{ title: 'Dashboard' }} 
      />
      <Tab.Screen 
        name="Notifications" 
        component={NotificationsScreen} 
        options={{ title: 'Alerts' }} 
      />
    </Tab.Navigator>
  );
};
