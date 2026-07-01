import { StatusBar } from 'expo-status-bar';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

const highlights = [
  'Student dashboards',
  'Teacher workflows',
  'Admin controls',
  'FastAPI backend integration',
];

export default function App() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.hero}>
          <Text style={styles.kicker}>School Sphere</Text>
          <Text style={styles.title}>Mobile foundation for school operations</Text>
          <Text style={styles.subtitle}>
            A production-ready Expo starting point for attendance, assignments,
            notices, and student management.
          </Text>
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>What this app will cover</Text>
          {highlights.map((item) => (
            <View key={item} style={styles.row}>
              <View style={styles.dot} />
              <Text style={styles.rowText}>{item}</Text>
            </View>
          ))}
        </View>

        <View style={styles.panelAccent}>
          <Text style={styles.panelTitle}>Next step</Text>
          <Text style={styles.panelText}>
            Build login flow, wire the API client, and add role-based navigation
            for students, teachers, and administrators.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#07111f',
  },
  container: {
    flexGrow: 1,
    padding: 24,
    gap: 16,
  },
  hero: {
    paddingTop: 24,
    paddingBottom: 8,
  },
  kicker: {
    color: '#7dd3fc',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 1.2,
    textTransform: 'uppercase',
    marginBottom: 12,
  },
  title: {
    color: '#f8fafc',
    fontSize: 36,
    lineHeight: 42,
    fontWeight: '800',
    marginBottom: 12,
  },
  subtitle: {
    color: '#cbd5e1',
    fontSize: 16,
    lineHeight: 24,
  },
  panel: {
    backgroundColor: '#0f1c2e',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1f2a3d',
  },
  panelAccent: {
    backgroundColor: '#12263f',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1e3a5f',
  },
  panelTitle: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
  },
  panelText: {
    color: '#dbeafe',
    fontSize: 15,
    lineHeight: 22,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#38bdf8',
    marginRight: 12,
  },
  rowText: {
    color: '#e2e8f0',
    fontSize: 15,
  },
});
