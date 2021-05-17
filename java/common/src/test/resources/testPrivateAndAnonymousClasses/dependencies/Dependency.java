public class Dependency {
    interface TestInterface {
        public void interfaceMethod();
    }

    public void method() {
        class PrivateClass implements TestInterface {
            public void interfaceMethod() {
                privateClassMethod();
            }

            private void privateClassMethod() {
                System.out.println("private class");
            }
        }
        TestInterface privateClass = new PrivateClass();
        privateClass.interfaceMethod();

        TestInterface anonymousClass = new TestInterface() {
            public void interfaceMethod() {
                anonymousClassMethod();
            }

            private void anonymousClassMethod() {
                System.out.println("anonymous class");
            }
        };
        anonymousClass.interfaceMethod();
    }
}
