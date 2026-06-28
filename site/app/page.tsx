import Nav from '@/components/Nav';
import Hero from '@/components/Hero';
import ProblemSolution from '@/components/ProblemSolution';
import SpecStrip from '@/components/SpecStrip';
import HowItWorks from '@/components/HowItWorks';
import Platforms from '@/components/Platforms';
import Quickstart from '@/components/Quickstart';
import AgentGrid from '@/components/AgentGrid';
import SkillGrid from '@/components/SkillGrid';
import CtaBand from '@/components/CtaBand';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <ProblemSolution />
        <SpecStrip />
        <HowItWorks />
        <Platforms />
        <Quickstart />
        <AgentGrid />
        <SkillGrid />
        <CtaBand />
      </main>
      <Footer />
    </>
  );
}
