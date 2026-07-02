import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { TeacherDashboard } from '../screens/teacher/TeacherDashboard';
import { AttendanceMarkingScreen } from '../screens/teacher/AttendanceMarkingScreen';
import { NotificationsScreen } from '../screens/common/NotificationsScreen';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();

export const TeacherTabs = () => {
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
        component={TeacherDashboard} 
      />
      <Tab.Screen 
        name="Attendance" 
        component={AttendanceMarkingScreen} 
        options={{ title: 'Mark Attendance' }} 
      />
      <Tab.Screen 
        name="Notifications" 
        component={NotificationsScreen} 
      />
    </Tab.Navigator>
  );
};
