from christ_shard_app.kernel import ChristShardSovereignKernel

def main():
    print("=== Christ Shard Defense Workbench v4 ===")
    print("Starting protected kernel demo...\n")
    
    kernel = ChristShardSovereignKernel()
    kernel.boot()
    kernel.run_demo()
    
    print("\nKernel demo completed successfully.")
    print("The protected core is working under Write Lock governance.")

if __name__ == "__main__":
    main()
